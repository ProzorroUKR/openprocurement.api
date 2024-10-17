from logging import getLogger

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


def parse_offset(offset: str):
    parts = offset.split(".")
    if len(parts) == 2 and len(parts[1]) == 10:  # timestamp offset format (for public_ts field)
        seconds, ordinal = parts
        return Timestamp(int(seconds), int(ordinal))
    try:
        # timestamp offset format (for "public_modified" field)
        return float(offset)
    except ValueError:
        # Used deprecated offset in iso format
        return parse_date(offset.replace(" ", "+")).timestamp()


def compose_offset(offset: float | Timestamp) -> str:
    # if request.user_agent in DEPRECATED_FEED_USER_AGENTS:  # can we drop this please ?
    #     # Use deprecated offset in iso format
    #     return datetime.fromtimestamp(offset).astimezone(TZ).isoformat()
    if isinstance(offset, Timestamp):
        # Timestamp(1721045886, 4)        -> '1721045886.000004'
        # Timestamp(1721045886, 1234567)  -> '1721045886.1234567'
        return f"{offset.time}.{offset.inc:010}"
    else:
        # offset in timestamp format "seconds.milliseconds"
        return str(offset)


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

        # offset param
        offset = None
        offset_param = self.request.params.get("offset")
        if offset_param:
            try:
                offset = parse_offset(offset_param)
            except ValueError:
                raise_operation_error(
                    self.request,
                    f"Invalid offset provided: {offset_param}",
                    status=404,
                    location="querystring",
                    name="offset",
                )
            params["offset"] = compose_offset(offset)

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
        timestamp_offset_field = "public_ts"
        depr_offset_field = "public_modified"

        # call db method
        results = self.db_listing_method(
            offset_field=depr_offset_field if isinstance(offset, float) else timestamp_offset_field,
            offset_value=offset,
            fields=db_fields | {timestamp_offset_field},
            descending=params.get("descending"),
            limit=params.get("limit", self.default_limit),
            mode=params.get("mode"),
            filters=filters,
        )

        # prepare response
        if results:
            params["offset"] = compose_offset(results[-1][timestamp_offset_field])
            prev_params["offset"] = compose_offset(results[0][timestamp_offset_field])
            for r in results:
                r.pop(timestamp_offset_field)
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
