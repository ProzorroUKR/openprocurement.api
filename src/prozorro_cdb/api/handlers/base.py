from hashlib import md5
from typing import Any, Callable, Dict, Literal

from aiohttp import web
from aiohttp.web_response import StreamResponse
from aiohttp_pydantic import PydanticView
from aiohttp_pydantic.decorator import inject_params
from aiohttp_pydantic.injectors import CONTEXT
from aiohttp_pydantic.oas.typing import r200
from pydantic import ValidationError
from yarl import URL

from openprocurement.api.procedure.utils import parse_date
from prozorro_cdb.api.context import url_to_absolute
from prozorro_cdb.api.errors import (
    JsonHTTPBadRequest,
    JsonHTTPNotFound,
    ModelValidationHttpError,
)
from prozorro_cdb.api.handlers.schema.feed import ListingResponseModel


@inject_params.and_request
async def get_version(request) -> web.Response:
    project_info = request.app["project_info"]["project"]
    return web.json_response(
        {
            "version": project_info["version"],
        }
    )


@inject_params
async def ping() -> web.Response:
    return web.json_response({"msg": "pong"})


def json_response_error(exception: ValidationError, context: CONTEXT | Literal["Unknown"]) -> StreamResponse:
    errors = exception.errors(include_url=False)
    for error in errors:
        if "ctx" in error and "error" in error["ctx"]:
            error["ctx"]["error"] = str(error["ctx"]["error"])

    return ModelValidationHttpError(details=f"Validation errors in {context}", errors=errors)


class BaseView(PydanticView):
    async def on_validation_error(
        self,
        exception: ValidationError,
        context: CONTEXT,
    ) -> StreamResponse:
        """
        This method is a hook to intercept ValidationError.

        This hook can be redefined to return a custom HTTP response error.
        The exception is a pydantic.ValidationError and the context is "body",
        "headers", "path" or "query string"
        """
        return json_response_error(exception, context)


def parse_offset(offset: str) -> tuple[float, int, str]:
    skip_len = 0
    skip_hash = ""

    parts = offset.split(".")
    if len(parts) == 4:
        skip_len = int(parts[2])
        skip_hash = parts[3]

    try:  # timestamp offset format (for "public_modified" field)
        offset_value = float(".".join(parts[:2]))
    except ValueError:
        # deprecated format
        offset_value = parse_date(offset.replace(" ", "+")).timestamp()
        return offset_value, skip_len, skip_hash
    else:
        return offset_value, skip_len, skip_hash


def get_offset_params(offset: float, items: list[dict[str, Any]], offset_field: str) -> tuple[str, int]:
    offset_item_ids = sorted(r["id"] for r in items if r[offset_field] == offset)
    skip_hash = md5("".join(offset_item_ids).encode()).hexdigest()
    skip_len = len(offset_item_ids)
    return skip_hash, skip_len


def compose_offset(offset: float, items: list[dict[str, Any]], offset_field: str) -> str:
    skip_hash, skip_len = get_offset_params(offset, items, offset_field)
    return f"{offset}.{skip_len}.{skip_hash}"


class MongodbResourceListingAsync(BaseView):
    view_name: str
    listing_default_fields = {"dateModified"}
    listing_allowed_fields = {"dateModified", "created", "modified"}
    default_limit = 100
    max_limit = 1000

    db_listing_method: Callable
    filter_key: str | None = None

    async def get(self) -> r200[ListingResponseModel]:
        params = {}
        filters = {}
        keys = {}
        request: web.Request = self.request

        # filter
        if self.filter_key:
            filter_value = request._match_info[self.filter_key]
            filters[self.filter_key] = filter_value
            keys[self.filter_key] = filter_value

        if mode := request.query.get("mode"):
            params["mode"] = mode

        # parse offset param
        skip_len = 0
        offset_value = 0.0
        skip_hash = ""
        if offset_param := request.query.get("offset"):
            try:
                offset_value, skip_len, skip_hash = parse_offset(offset_param)
            except ValueError:
                raise JsonHTTPNotFound(
                    details="Invalid offset provided",
                    offset=offset_param,
                    location="querystring",
                    name="offset",
                )

        if limit_param := request.query.get("limit"):
            try:
                limit = int(limit_param)
            except ValueError as e:
                raise JsonHTTPBadRequest(
                    details=e.args[0],
                    location="querystring",
                    name="limit",
                )
            else:
                params["limit"] = min(limit, self.max_limit)

        # descending param
        if request.query.get("descending"):
            params["descending"] = 1

        # opt_fields param
        opt_fields = set()
        if request.query.get("opt_fields"):
            opt_fields = set(request.query.get("opt_fields", "").split(",")) & self.listing_allowed_fields
            filtered_fields = opt_fields - self.listing_default_fields
            if filtered_fields:
                params["opt_fields"] = ",".join(sorted(filtered_fields))

        # prev_page
        prev_params = {**params}
        if params.get("descending"):
            del prev_params["descending"]
        else:
            prev_params["descending"] = 1

        data_fields = opt_fields | self.listing_default_fields
        db_fields = self.db_fields(data_fields)
        time_offset_field = "public_modified"

        try:
            limit_results = int(params.get("limit", self.default_limit))
        except ValueError:
            limit_results = self.default_limit

        # call db method
        results = await self.db_listing_method(
            offset_field=time_offset_field,
            offset_value=offset_value,
            fields=db_fields | {time_offset_field},
            descending=params.get("descending"),
            limit=limit_results + skip_len,  # + offset items length
            mode=params.get("mode"),
            filters=filters,
            inclusive_filter=skip_len > 0,
        )

        # find same offset results and skip them if already seen
        if results and skip_len:  # should be always the case with new offsets
            actual_skip_hash, actual_skip_len = get_offset_params(offset_value, results, time_offset_field)
            # we only "hide" items with provided 'offset_value', when their ids hash is equal to the expected
            if actual_skip_len == skip_len and actual_skip_hash == skip_hash:
                results = [r for r in results if r[time_offset_field] != offset_value]

        # prepare response
        if results:
            params["offset"] = compose_offset(results[-1][time_offset_field], results, time_offset_field)
            prev_params["offset"] = compose_offset(results[0][time_offset_field], results, time_offset_field)

            if time_offset_field not in opt_fields:
                for r in results:
                    r.pop(time_offset_field)
        elif offset_param:
            params["offset"] = offset_param  # remain the same if there is no results

        router = request.app.router
        base_url = router[self.view_name].url_for(**keys)
        data = {
            "data": self.filter_results_fields(results, data_fields),
            "next_page": self.get_page(base_url, params),
        }
        if request.query.get("descending") or request.query.get("offset"):
            data["prev_page"] = self.get_page(base_url, prev_params)
        return data

    def get_page(self, base_url: URL, params: Dict[str, Any]):
        path = str(base_url.with_query(params))
        return {
            "offset": params.get("offset", ""),
            "path": path,
            "uri": url_to_absolute(path, add_prefix=False),
        }

    def db_fields(self, fields):
        return fields

    def filter_results_fields(self, results, fields):
        all_fields = fields | {"id"}
        for r in results:
            for k in list(r.keys()):
                if k not in all_fields:
                    del r[k]
        return results
