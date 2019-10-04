# -*- coding: utf-8 -*-
from functools import partial
from hashlib import sha512
from logging import getLogger
from cornice.resource import resource
from schematics.exceptions import ModelValidationError

from openprocurement.api.constants import ROUTE_PREFIX
from openprocurement.api.utils import error_handler, context_unpack
from openprocurement.api.models import get_now

from openprocurement.relocation.api.traversal import factory
from openprocurement.relocation.api.models import Transfer


transferresource = partial(resource, error_handler=error_handler, factory=factory)

LOGGER = getLogger("openprocurement.relocation.api")


def extract_transfer(request, transfer_id=None):
    db = request.registry.db
    if not transfer_id:
        transfer_id = request.matchdict["transfer_id"]
    doc = db.get(transfer_id)
    if doc is None or doc.get("doc_type") != "Transfer":
        request.errors.add("url", "transfer_id", "Not Found")
        request.errors.status = 404
        raise error_handler(request.errors)

    return request.transfer_from_data(doc)


def transfer_from_data(request, data):
    return Transfer(data)


def save_transfer(request):
    """ Save transfer object to database
    :param request:
    :return: True if Ok
    """
    transfer = request.validated["transfer"]
    transfer.date = get_now()
    try:
        transfer.store(request.registry.db)
    except ModelValidationError as e:  # pragma: no cover
        for i in e.message:
            request.errors.add("body", i, e.message[i])
        request.errors.status = 422
    except Exception as e:  # pragma: no cover
        request.errors.add("body", "data", str(e))
    else:
        LOGGER.info(
            "Saved transfer {}: at {}".format(transfer.id, get_now().isoformat()),
            extra=context_unpack(request, {"MESSAGE_ID": "save_transfer"}),
        )
        return True


def set_ownership(item, request, access_token=None, transfer_token=None):
    item.owner = request.authenticated_userid
    item.access_token = sha512(access_token).hexdigest()
    item.transfer_token = sha512(transfer_token).hexdigest()


def update_ownership(tender, transfer):
    tender.owner = transfer.owner
    tender.owner_token = transfer.access_token
    tender.transfer_token = transfer.transfer_token


def get_transfer_location(request, route_name, *args, **kwargs):
    location = request.route_path(route_name, *args, **kwargs)
    return location[len(ROUTE_PREFIX) :]
