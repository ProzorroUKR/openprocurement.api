from logging import getLogger

from openprocurement.api.constants import ROUTE_PREFIX
from openprocurement.api.utils import error_handler

LOGGER = getLogger("openprocurement.relocation.api")


def extract_transfer_doc(request, transfer_id=None):
    if not transfer_id:
        transfer_id = request.matchdict["transfer_id"]
    doc = request.registry.mongodb.transfers.get(transfer_id)
    if doc is None:
        request.errors.add("url", "transfer_id", "Not Found")
        request.errors.status = 404
        raise error_handler(request)

    return doc


def get_transfer_location(request, route_name, *args, **kwargs):
    location = request.route_path(route_name, *args, **kwargs)
    return location[len(ROUTE_PREFIX) :]
