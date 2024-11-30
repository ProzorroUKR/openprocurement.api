from hashlib import md5
from logging import getLogger
from typing import Any

from bson import Timestamp

from openprocurement.api.constants import CRITICAL_HEADERS_LOG_ENABLED
from openprocurement.api.context import set_now, set_request
from openprocurement.api.mask import mask_object_data
from openprocurement.api.procedure.utils import parse_date
from openprocurement.api.utils import context_unpack, json_view, raise_operation_error


class BaseResource:
    def __init__(self, request, context=None):
        self.context = context
        self.request = request
        self.server_id = request.registry.server_id
        self.LOGGER = getLogger(type(self).__module__)

        set_request(request)
        set_now()

        if CRITICAL_HEADERS_LOG_ENABLED:  # for additional investigation if needed
            self.LOGGER.info("Log request", extra=context_unpack(self.request, {}))


def parse_offset(offset: str) -> tuple[Timestamp | float, int, str]:
    skip_len = 0
    skip_hash = ""

    parts = offset.split(".")
    if len(parts) > 1 and len(parts[1]) == 10:  # timestamp offset format (for public_ts field)
        seconds, ordinal = parts[:2]
        offset_value = Timestamp(int(seconds), int(ordinal))
        if len(parts) == 4:
            skip_len, skip_hash = parts[2:]
            skip_len = int(skip_len)
        return offset_value, skip_len, skip_hash

    try:
        # timestamp offset format (for "public_modified" field)
        offset_value = float(offset)
    except ValueError:
        # Used deprecated offset in iso format
        offset_value = parse_date(offset.replace(" ", "+")).timestamp()

    return offset_value, skip_len, skip_hash


def get_offset_params(offset: Timestamp, items: list[dict[str, Any]], offset_field: str) -> tuple[str, int]:
    offset_item_ids = sorted(r["id"] for r in items if r[offset_field] == offset)
    skip_hash = md5("".join(offset_item_ids).encode()).hexdigest()
    skip_len = len(offset_item_ids)
    return skip_hash, skip_len


def compose_offset(offset: Timestamp, items: list[dict[str, Any]], offset_field: str) -> str:
    skip_hash, skip_len = get_offset_params(offset, items, offset_field)
    return f"{offset.time}.{offset.inc:010}.{skip_len}.{skip_hash}"


class MongodbResourceListing(BaseResource):
    listing_name = "Items"
    listing_default_fields = {"dateModified"}
    listing_allowed_fields = {"dateModified", "created", "modified"}
    default_limit = 100
    max_limit = 1000

    db_listing_method: callable
    filter_key = None

    @json_view(permission="view_listing")
    def get(self):
        params = {}
        filters = {}
        keys = {}

        # filter
        if self.filter_key:
            filter_value = self.request.matchdict[self.filter_key]
            filters[self.filter_key] = filter_value
            keys[self.filter_key] = filter_value

        # mode param
        if self.request.params.get("mode"):
            params["mode"] = self.request.params.get("mode")

        # parse offset param
        skip_len = 0
        offset_value = skip_hash = None
        offset_param = self.request.params.get("offset")
        if offset_param:
            try:
                offset_value, skip_len, skip_hash = parse_offset(offset_param)
            except ValueError:
                raise_operation_error(
                    self.request,
                    f"Invalid offset provided: {offset_param}",
                    status=404,
                    location="querystring",
                    name="offset",
                )

        # limit param
        limit_param = self.request.params.get("limit")
        if limit_param:
            try:
                limit = int(limit_param)
            except ValueError as e:
                raise_operation_error(
                    self.request,
                    e.args[0],
                    status=400,
                    location="querystring",
                    name="limit",
                )
            else:
                params["limit"] = min(limit, self.max_limit)

        # descending param
        if self.request.params.get("descending"):
            params["descending"] = 1

        # opt_fields param
        if self.request.params.get("opt_fields"):
            opt_fields = set(self.request.params.get("opt_fields", "").split(",")) & self.listing_allowed_fields
            filtered_fields = opt_fields - self.listing_default_fields
            if filtered_fields:
                params["opt_fields"] = ",".join(sorted(filtered_fields))
        else:
            opt_fields = set()

        # prev_page
        prev_params = {**params}
        if params.get("descending"):
            del prev_params["descending"]
        else:
            prev_params["descending"] = 1

        data_fields = opt_fields | self.listing_default_fields
        db_fields = self.db_fields(data_fields)
        ts_offset_field = "public_ts"
        depr_offset_field = "public_modified"

        # call db method
        limit_results = params.get("limit", self.default_limit)
        results = self.db_listing_method(
            offset_field=depr_offset_field if isinstance(offset_value, float) else ts_offset_field,
            offset_value=offset_value,
            fields=db_fields | {ts_offset_field},
            descending=params.get("descending"),
            limit=limit_results + skip_len,  # + offset items length
            mode=params.get("mode"),
            filters=filters,
            inclusive_filter=skip_len > 0,
        )

        # find same offset results and skip them if already seen
        if results and skip_len:  # should be always the case with new offsets
            actual_skip_hash, actual_skip_len = get_offset_params(offset_value, results, ts_offset_field)
            # we only "hide" items with provided 'offset_value', when their ids hash is equal to the expected
            if actual_skip_len == skip_len and actual_skip_hash == skip_hash:
                results = [r for r in results if r[ts_offset_field] != offset_value]

        # prepare response
        if results:
            params["offset"] = compose_offset(results[-1][ts_offset_field], results, ts_offset_field)
            prev_params["offset"] = compose_offset(results[0][ts_offset_field], results, ts_offset_field)

            for r in results:
                r.pop(ts_offset_field)
        elif offset_param:
            params["offset"] = offset_param  # remain the same if there is no results

        data = {
            "data": self.filter_results_fields(results, data_fields),
            "next_page": self.get_page(keys, params),
        }
        if self.request.params.get("descending") or self.request.params.get("offset"):
            data["prev_page"] = self.get_page(keys, prev_params)

        return data

    def get_page(self, keys, params):
        return {
            "offset": params.get("offset", ""),
            "path": self.request.route_path(self.listing_name, _query=params, **keys),
            "uri": self.request.route_url(self.listing_name, _query=params, **keys),
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


class RestrictedResourceListingMixin:
    mask_mapping = {}
    request = None

    def db_fields(self, fields):
        fields = super().db_fields(fields)
        return fields | {"config"}

    def filter_results_fields(self, results, fields):
        for r in results:
            mask_object_data(self.request, r, mask_mapping=self.mask_mapping)
        results = super().filter_results_fields(results, fields)
        return results
