# -*- coding: utf-8 -*-
from decimal import Decimal, ROUND_FLOOR

from openprocurement.api.utils import (
    raise_operation_error,
    to_decimal,
)
from openprocurement.api.validation import (
    _validate_accreditation_level,
    OPERATIONS,
)
from openprocurement.tender.core.procedure.validation import (
    validate_update_contract_value,
    validate_update_contract_value_amount,
    validate_update_contract_value_net_required,
)
from openprocurement.contracting.core.utils import get_transaction_by_id
from openprocurement.contracting.core.procedure.utils import is_tender_owner, is_contract_owner, is_bid_owner


def _validate_contract_accreditation_level(request, model):
    _validate_accreditation_level(request, model.create_accreditations, "contract", "creation")


# changes
def validate_contract_change_add_not_in_allowed_contract_status(request, **kwargs):
    contract = request.validated["contract"]
    if contract["status"] not in ["pending", "active"]:
        raise_operation_error(
            request, f"Can't add contract change in current ({contract['status']}) contract status"
        )


def validate_create_contract_change(request, **kwargs):
    contract = request.validated["contract"]
    if contract.get("changes") and contract["changes"][-1]["status"] == "pending":
        raise_operation_error(request, "Can't create new contract change while any (pending) change exists")


def validate_contract_change_update_not_in_allowed_change_status(request, **kwargs):
    change = request.validated["change"]
    if change["status"] == "active":
        raise_operation_error(request, f"Can't update contract change in current ({change['status']}) status")


# contract
def validate_contract_update_not_in_allowed_status(request, **_):
    contract = request.validated["contract"]
    if contract["status"] not in ["pending", "active"]:
        raise_operation_error(request, f"Can't update contract in current ({contract['status']}) status")



def validate_credentials_generate(request, **_):
    contract = request.validated["contract"]
    if contract["status"] not in ["pending", "active"]:
        raise_operation_error(
            request, f"Can't generate credentials in current ({contract['status']}) contract status"
        )


# contract document
def validate_contract_document_operation_not_in_allowed_contract_status(request, **_):
    if request.validated["contract"]["status"] not in ["pending", "active"]:
        raise_operation_error(
            request,
            f"Can't {OPERATIONS.get(request.method)} document in current "
            f"({request.validated['contract']['status']}) contract status"
        )


def validate_add_document_to_active_change(request, **_):
    data = request.validated["data"]
    if "relatedItem" in data and data.get("documentOf") == "change":
        changes = request.validated["contract"].get("changes", "")
        if not any(c["id"] == data["relatedItem"] and c["status"] == "pending" for c in changes):
            raise_operation_error(request, "Can't add document to 'active' change")


# Signer info

def validate_signer_info_update_in_not_allowed_status(request, **_):
    contract = request.validated["contract"]
    if contract["status"] != "pending":
        raise_operation_error(request, f"Can't update contract signerInfo in current ({contract['status']}) status")


# Access
def validate_tender_owner(request, **_):
    contract = request.validated["contract"]
    if not is_tender_owner(request, contract):
        raise_operation_error(
            request,
            "Forbidden",
            location="url",
            name="permission"
        )


def validate_contract_owner(request, **_):
    contract = request.validated["contract"]
    if not is_contract_owner(request, contract):
        raise_operation_error(
            request,
            "Forbidden",
            location="url",
            name="permission"
        )


def validate_contract_supplier(request, **_):
    contract = request.validated["contract"]
    if not is_bid_owner(request, contract):
        raise_operation_error(
            request,
            "Forbidden",
            location="url",
            name="permission"
        )


def validate_contract_participant(request, **_):
    contract = request.validated["contract"]

    if (
        not is_contract_owner(request, contract)
        and not is_bid_owner(request, contract)
    ):
        raise_operation_error(
            request,
            "Forbidden",
            location="url",
            name="permission"
        )
