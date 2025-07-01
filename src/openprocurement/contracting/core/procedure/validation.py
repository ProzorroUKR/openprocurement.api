from openprocurement.api.procedure.models.document import ConfidentialityType
from openprocurement.api.utils import raise_operation_error
from openprocurement.api.validation import OPERATIONS, validate_accreditation_level_base
from openprocurement.contracting.core.procedure.utils import (
    is_bid_owner,
    is_contract_owner,
    is_tender_owner,
)


def _validate_contract_accreditation_level(request, model):
    validate_accreditation_level_base(request, model.create_accreditations, "contract", "creation")


# changes
def validate_contract_change_action_not_in_allowed_contract_status(request, **kwargs):
    contract = request.validated["contract"]
    if contract["status"] != "active":
        raise_operation_error(
            request,
            f"Can't {OPERATIONS.get(request.method)} contract change in current ({contract['status']}) contract status",
        )


def validate_create_contract_change(request, **kwargs):
    contract = request.validated["contract"]
    if contract.get("changes") and contract["changes"][-1]["status"] == "pending":
        raise_operation_error(
            request,
            "Can't create new contract change while any (pending) change exists",
        )


def validate_contract_change_update_not_in_allowed_change_status(request, **kwargs):
    change = request.validated["change"]
    if change["status"] == "active":
        raise_operation_error(
            request,
            f"Can't update contract change in current ({change['status']}) status",
        )


# contract
def validate_contract_update_not_in_allowed_status(request, **_):
    contract = request.validated["contract"]
    if contract["status"] not in ["pending", "active"]:
        raise_operation_error(request, f"Can't update contract in current ({contract['status']}) status")


def validate_credentials_generate(request, **_):
    contract = request.validated["contract"]
    if contract["status"] not in ["pending", "active"]:
        raise_operation_error(
            request,
            f"Can't generate credentials in current ({contract['status']}) contract status",
        )


# contract document
def validate_contract_document_operation_not_in_allowed_contract_status(request, **_):
    if request.validated["contract"]["status"] not in ["pending", "active"]:
        raise_operation_error(
            request,
            f"Can't {OPERATIONS.get(request.method)} document in current "
            f"({request.validated['contract']['status']}) contract status",
        )


def validate_add_document_to_active_change(request, **_):
    data = request.validated["data"]
    if "relatedItem" in data and data.get("documentOf") == "change":
        changes = request.validated["contract"].get("changes", "")
        if not any(c["id"] == data["relatedItem"] and c["status"] == "pending" for c in changes):
            raise_operation_error(request, "Can't add document to 'active' change")


# Signer info


def validate_contract_in_pending_status(request, **_):
    contract = request.validated["contract"]
    if contract["status"] != "pending":
        raise_operation_error(
            request,
            f"Operation forbidden in current ({contract['status']}) status",
        )


# Access
def validate_tender_owner(request, **_):
    contract = request.validated["contract"]
    if not is_tender_owner(request, contract):
        raise_operation_error(request, "Forbidden", location="url", name="permission")


def validate_contract_owner(request, **_):
    contract = request.validated["contract"]
    if not is_contract_owner(request, contract):
        raise_operation_error(request, "Forbidden", location="url", name="permission")


def validate_contract_supplier(request, **_):
    contract = request.validated["contract"]
    tender = request.validated["tender"]
    tender_type = tender["procurementMethodType"]
    limited_procedures = ("reporting", "negotiation", "negotiation.quick")

    if not (
        is_bid_owner(request, contract) or tender_type in limited_procedures and is_contract_owner(request, contract)
    ):
        raise_operation_error(request, "Forbidden", location="url", name="permission")


def validate_contract_participant(request, **_):
    contract = request.validated["contract"]

    if not is_contract_owner(request, contract) and not is_bid_owner(request, contract):
        raise_operation_error(request, "Forbidden", location="url", name="permission")


def validate_download_contract_document(request, **_):
    if request.params.get("download"):
        document = request.validated["document"]
        if document.get("confidentiality", "") == ConfidentialityType.BUYER_ONLY and not is_contract_owner(
            request, request.validated["contract"]
        ):
            raise_operation_error(request, "Document download forbidden.")


def validate_contract_signature_operation(request, **_):
    contract = request.validated["contract"]
    data = request.validated["data"][0] if isinstance(request.validated["data"], list) else request.validated["data"]
    # get documentType from request data if it was mentioned or from previously created document during patch
    document_type = data.get("documentType") or request.validated.get("document", {}).get("documentType")
    if document_type == "contractSignature" and contract["status"] != "pending":
        raise_operation_error(
            request,
            f"Can't {OPERATIONS.get(request.method)} sign document in current "
            f"({request.validated['contract']['status']}) contract status",
        )
