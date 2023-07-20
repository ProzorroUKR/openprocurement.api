# -*- coding: utf-8 -*-
from functools import partial
from logging import getLogger
from hashlib import sha512
from cornice.resource import resource
from schematics.types import StringType

from openprocurement.api.mask import mask_object_data
from openprocurement.api.utils import (
    error_handler,
    context_unpack,
    apply_data_patch,
    generate_id,
    get_now,
    handle_store_exceptions,
    check_document,
    update_document_url,
)
from openprocurement.api.auth import extract_access_token

from openprocurement.contracting.api.traversal import factory
from openprocurement.contracting.api.models import Contract
from openprocurement.tender.core.procedure.utils import append_revision, get_revision_changes, set_mode_test_titles


LOGGER = getLogger("openprocurement.contracting.api.procedure")


def save_contract(request, insert=False, contract=None, contract_src=None):
    if contract is None:
        contract = request.validated["contract"]
    if contract_src is None:
        contract_src = request.validated["contract_src"]

    if contract.get("mode", "") == "test":
        set_mode_test_titles(contract)

    patch = get_revision_changes(contract, contract_src)
    if patch:
        now = get_now()
        append_revision(request, contract, patch)

        old_date_modified = contract.get("dateModified", now.isoformat())
        with handle_store_exceptions(request):
            request.registry.mongodb.contracts.save(
                contract,
                insert=insert,
                modified=True,
            )
            LOGGER.info(
                "Saved contract {}: dateModified {} -> {}".format(
                    contract["_id"],
                    old_date_modified,
                    contract["dateModified"]
                ),
                extra=context_unpack(request, {"MESSAGE_ID": "save_contract"}, {"CONTRACT_REV": contract["_rev"]}),
            )
            return True


def is_tender_owner(request, contract):
    acc_token = extract_access_token(request)
    tender_token = contract["tender_token"]
    if len(tender_token) != len(acc_token):
        acc_token = sha512(acc_token.encode("utf-8")).hexdigest()
    return request.authenticated_userid == contract["owner"] and acc_token == tender_token
