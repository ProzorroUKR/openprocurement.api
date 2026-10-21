from logging import getLogger

from openprocurement.api.constants import ROUTE_PREFIX
from openprocurement.api.utils import get_obj_by_id

LOGGER = getLogger("openprocurement.relocation.api")


def extract_transfer_doc(request, transfer_id=None):
    if not transfer_id:
        transfer_id = request.matchdict["transfer_id"]
    return get_obj_by_id(request, "transfers", transfer_id)


def get_transfer_location(request, route_name, *args, **kwargs):
    location = request.route_path(route_name, *args, **kwargs)
    return location[len(ROUTE_PREFIX) :]
