from hashlib import sha512
from logging import getLogger
from uuid import uuid4

from openprocurement.api.context import get_now
from openprocurement.api.utils import context_unpack, handle_store_exceptions

LOGGER = getLogger("openprocurement.relocation.api")


def save_transfer(request, insert=False):
    transfer = request.validated["transfer"]
    transfer["date"] = get_now().isoformat()

    with handle_store_exceptions(request):
        request.registry.mongodb.transfers.save(transfer, insert=insert)
        LOGGER.info(
            "Saved transfer {}: at {}".format(transfer["_id"], get_now().isoformat()),
            extra=context_unpack(request, {"MESSAGE_ID": "save_transfer"}),
        )
        return True


def set_ownership(item, request):
    token, transfer = uuid4().hex, uuid4().hex
    item["owner"] = request.authenticated_userid
    item["access_token"] = token
    item["transfer_token"] = sha512(transfer.encode("utf-8")).hexdigest()
    access = {"token": token, "transfer": transfer}
    return access


def update_ownership(tender, transfer):
    tender["owner"] = transfer["owner"]
    tender["owner_token"] = transfer["access_token"]
    tender["transfer_token"] = transfer["transfer_token"]
