# -*- coding: utf-8 -*-
from functools import partial
from hashlib import sha512
from logging import getLogger
from cornice.resource import resource

from openprocurement.api.constants import ROUTE_PREFIX
from openprocurement.api.utils import error_handler, context_unpack, handle_store_exceptions
from openprocurement.api.models import get_now

from openprocurement.relocation.api.traversal import factory
from openprocurement.relocation.api.models import Transfer


transferresource = partial(resource, error_handler=error_handler, factory=factory)

LOGGER = getLogger("openprocurement.relocation.api")


def extract_transfer(request, transfer_id=None):
    if not transfer_id:
        transfer_id = request.matchdict["transfer_id"]
    doc = request.registry.mongodb.transfers.get(transfer_id)
    if doc is None:
        request.errors.add("url", "transfer_id", "Not Found")
        request.errors.status = 404
        raise error_handler(request)

    return request.transfer_from_data(doc)


def transfer_from_data(request, data):
    return Transfer(data)


def save_transfer(request, insert=False):
    transfer = request.validated["transfer"]
    transfer.date = get_now()

    with handle_store_exceptions(request):
        request.registry.mongodb.transfers.save(transfer, insert=insert)
        LOGGER.info(
            "Saved transfer {}: at {}".format(transfer.id, get_now().isoformat()),
            extra=context_unpack(request, {"MESSAGE_ID": "save_transfer"}),
        )
        return True


def set_ownership(item, request, access_token=None, transfer_token=None):
    item.owner = request.authenticated_userid
    item.access_token = access_token
    item.transfer_token = sha512(transfer_token.encode("utf-8")).hexdigest()


def update_ownership(tender, transfer):
    tender.owner = transfer.owner
    tender.owner_token = transfer.access_token
    tender.transfer_token = transfer.transfer_token


def get_transfer_location(request, route_name, *args, **kwargs):
    location = request.route_path(route_name, *args, **kwargs)
    return location[len(ROUTE_PREFIX) :]
