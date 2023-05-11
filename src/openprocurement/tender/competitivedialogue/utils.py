# -*- coding: utf-8 -*-
from logging import getLogger
from hashlib import sha512
from schematics.types import StringType

from openprocurement.api.utils import (
    context_unpack,
    generate_id,
    raise_operation_error,
    set_ownership as api_set_ownership,
)
from openprocurement.tender.core.utils import (
    save_tender,
)
from openprocurement.tender.competitivedialogue.constants import MINIMAL_NUMBER_OF_BIDS

LOGGER = getLogger(__name__)


def set_ownership(item):
    item.owner_token = generate_id()
    access = {"token": item.owner_token}
    if isinstance(getattr(type(item), "transfer_token", None), StringType):
        transfer = generate_id()
        item.transfer_token = sha512(transfer.encode("utf-8")).hexdigest()
        access["transfer"] = transfer
    return access


def prepare_shortlistedFirms(shortlistedFirms):
    """ Make list with keys
        key = {identifier_id}_{identifier_scheme}_{lot_id}
    """
    all_keys = set()
    for firm in shortlistedFirms:
        key = "{firm_id}_{firm_scheme}".format(
            firm_id=firm["identifier"]["id"], firm_scheme=firm["identifier"]["scheme"]
        )
        if firm.get("lots"):
            keys = set("{key}_{lot_id}".format(key=key, lot_id=lot["id"]) for lot in firm.get("lots"))
        else:
            keys = {key}
        all_keys |= keys
    return all_keys


def prepare_author(obj):
    """ Make key
        {author.identifier.id}_{author.identifier.scheme}
        or
        {author.identifier.id}_{author.identifier.scheme}_{id}
        if obj has relatedItem and questionOf != tender or obj has relatedLot than
    """
    base_key = "{id}_{scheme}".format(
        scheme=obj["author"]["identifier"]["scheme"],
        id=obj["author"]["identifier"]["id"],
    )
    related_id = None
    if obj.get("relatedLot"):
        related_id = obj.get("relatedLot")
    elif (obj.get("relatedItem") and obj.get("questionOf") in ("lot", "item")):
        related_id = obj.get("relatedItem")
    if related_id:
        base_key = "{base_key}_{id}".format(
            base_key=base_key,
            id=related_id,
        )
    return base_key


def prepare_bid_identifier(bid):
    """ Make list with keys
        key = {identifier_id}_{identifier_scheme}_{lot_id}
    """
    all_keys = set()
    for tenderer in bid["tenderers"]:
        key = "{id}_{scheme}".format(id=tenderer["identifier"]["id"], scheme=tenderer["identifier"]["scheme"])
        if bid.get("lotValues"):
            keys = set("{key}_{lot_id}".format(key=key, lot_id=lot["relatedLot"]) for lot in bid.get("lotValues"))
        else:
            keys = {key}
        all_keys |= keys
    return all_keys


def get_item_by_id(tender, item_id):
    for item in tender["items"]:
        if item["id"] == item_id:
            return item
