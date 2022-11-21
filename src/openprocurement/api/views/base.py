from datetime import datetime

from openprocurement.api.constants import DEPRECATED_FEED_USER_AGENTS, TZ
from openprocurement.api.context import set_request, set_now
from openprocurement.api.utils import parse_date, json_view, LOGGER, raise_operation_error
from logging import getLogger


class BaseResource:

    def __init__(self, request, context=None):
        self.context = context
        self.request = request
        self.server_id = request.registry.server_id
        self.LOGGER = getLogger(type(self).__module__)

        set_request(request)
        set_now()


def parse_offset(offset: str):
    try:
        # Used new offset in timestamp format
        return float(offset)
    except ValueError:
        # Used deprecated offset in iso format
        return parse_date(offset.replace(" ", "+")).timestamp()


def compose_offset(request, offset: float):
    if request.user_agent in DEPRECATED_FEED_USER_AGENTS:
        # Use deprecated offset in iso format
        return datetime.fromtimestamp(offset).astimezone(TZ).isoformat()
    else:
        # Use new offset in timestamp format
        return offset


class MongodbResourceListing(BaseResource):

    listing_name = "Items"
    offset_field = "public_modified"
    listing_default_fields = {"dateModified"}
    all_fields = {"dateModified", "created", "modified"}
    default_limit = 100
    max_limit = 1000
    db_listing_method: callable
    filter_key = None

    @json_view(permission='view_listing')
    def get(self):
        params = {}
        if self.request.params.get('mode'):
            params["mode"] = self.request.params.get('mode')

        filters = {}
        keys = {}
        if self.filter_key:
            filter_value = self.request.matchdict[self.filter_key]
            filters[self.filter_key] = filter_value
            keys[self.filter_key] = filter_value

        offset = None
        offset_param = self.request.params.get('offset')
        if offset_param:
            try:
                offset = parse_offset(offset_param)
            except ValueError:
                raise_operation_error(
                    self.request,
                    f"Invalid offset provided: {offset_param}",
                    status=404, location="querystring", name="offset")
            params["offset"] = compose_offset(self.request, offset)

        if self.request.params.get('limit'):
            try:
                limit = int(self.request.params.get('limit'))
            except ValueError as e:
                raise_operation_error(self.request, e.args[0], status=400, location="querystring", name="offset")
            else:
                params["limit"] = min(limit, self.max_limit)
        if self.request.params.get('descending'):
            params["descending"] = 1
        if self.request.params.get('opt_fields'):
            fields = set(self.request.params.get('opt_fields', '').split(",")) & self.all_fields
            filtered_fields = fields - self.listing_default_fields
            if filtered_fields:
                params["opt_fields"] = ",".join(filtered_fields)
        else:
            fields = set()

        prev_params = dict(**params)
        if params.get("descending"):
            del prev_params["descending"]
        else:
            prev_params["descending"] = 1

        # call db method
        results = self.db_listing_method(
            offset_field=self.offset_field,
            offset_value=offset,
            fields=fields | self.listing_default_fields,
            descending=params.get("descending"),
            limit=params.get("limit", self.default_limit),
            mode=params.get("mode"),
            filters=filters,
        )

        if results:
            params['offset'] = compose_offset(self.request, results[-1][self.offset_field])
            prev_params['offset'] = compose_offset(self.request, results[0][self.offset_field])
            if self.offset_field not in self.all_fields:
                for r in results:
                    r.pop(self.offset_field)
        data = {
            'data': [r for r in results],
            'next_page': {
                "offset": params.get("offset", ""),
                "path": self.request.route_path(self.listing_name, _query=params, **keys),
                "uri": self.request.route_url(self.listing_name, _query=params, **keys)
            }
        }
        if self.request.params.get('descending') or self.request.params.get('offset'):
            data['prev_page'] = {
                "offset": prev_params.get("offset", ""),
                "path": self.request.route_path(self.listing_name, _query=prev_params, **keys),
                "uri": self.request.route_url(self.listing_name, _query=prev_params, **keys)
            }

        return data
