# -*- coding: utf-8 -*-
from hashlib import sha512

from openprocurement.api.utils import update_logging_context, error_handler
from openprocurement.api.validation import (
    validate_json_data,
    validate_data,
    _validate_accreditation_level,
    _validate_accreditation_level_mode,
    _validate_accreditation_level_owner,
    _validate_accreditation_level_kind,
)
from openprocurement.relocation.api.models import Transfer


def validate_transfer_data(request, **kwargs):
    update_logging_context(request, {"transfer_id": "__new__"})
    data = validate_json_data(request)
    model = Transfer
    return validate_data(request, model, data=data)


def validate_ownership_data(request, **kwargs):
    data = validate_json_data(request)
    for field in ["id", "transfer"]:
        if not data.get(field):
            request.errors.add("body", field, "This field is required.")
    if request.errors:
        request.errors.status = 422
        raise error_handler(request)
    request.validated["ownership_data"] = data


def _validate_transfer_accreditation_level(request, obj, attr):
    levels = getattr(type(obj), attr)
    mode = obj.get("mode", None)
    _validate_accreditation_level(request, levels, "ownership", "change")
    _validate_accreditation_level_mode(request, mode, "ownership", "change")


def validate_tender_accreditation_level(request, **kwargs):
    tender = request.validated["tender"]
    model_attr = "transfer_accreditations" if hasattr(tender, "transfer_accreditations") else "create_accreditations"
    kind = tender.get("procuringEntity", {}).get("kind", "")
    _validate_transfer_accreditation_level(request, tender, model_attr)
    _validate_accreditation_level_kind(request, tender.central_accreditations, kind, "ownership", "change")


def validate_contract_accreditation_level(request, **kwargs):
    _validate_transfer_accreditation_level(request, request.validated["contract"], "create_accreditations")


def validate_plan_accreditation_level(request, **kwargs):
    _validate_transfer_accreditation_level(request, request.validated["plan"], "create_accreditations")


def validate_agreement_accreditation_level(request, **kwargs):
    _validate_transfer_accreditation_level(request, request.validated["agreement"], "create_accreditations")


def _validate_owner_accreditation_level(request, obj):
    _validate_accreditation_level_owner(request, obj.owner, "ownership", "ownership", "change")


def validate_tender_owner_accreditation_level(request, **kwargs):
    _validate_owner_accreditation_level(request, request.validated["tender"])


def validate_contract_owner_accreditation_level(request, **kwargs):
    _validate_owner_accreditation_level(request, request.validated["contract"])


def validate_plan_owner_accreditation_level(request, **kwargs):
    _validate_owner_accreditation_level(request, request.validated["plan"])


def validate_agreement_owner_accreditation_level(request, **kwargs):
    _validate_owner_accreditation_level(request, request.validated["agreement"])


def _validate_transfer_token(request, obj):
    token = request.validated["ownership_data"]["transfer"]
    if obj.transfer_token != sha512(token.encode("utf-8")).hexdigest():
        request.errors.add("body", "transfer", "Invalid transfer")
        request.errors.status = 403
        raise error_handler(request)


def validate_tender_transfer_token(request, **kwargs):
    _validate_transfer_token(request, request.validated["tender"])


def validate_contract_transfer_token(request, **kwargs):
    _validate_transfer_token(request, request.validated["contract"])


def validate_plan_transfer_token(request, **kwargs):
    _validate_transfer_token(request, request.validated["plan"])


def validate_agreement_transfer_token(request, **kwargs):
    _validate_transfer_token(request, request.validated["agreement"])


def validate_tender(request, **kwargs):
    tender = request.validated["tender"]
    if tender.status in [
        "complete",
        "unsuccessful",
        "cancelled",
        "active.stage2.waiting",
        "draft.pending",
        "draft.unsuccessful",
    ]:
        request.errors.add(
            "body", "data", "Can't update credentials in current ({}) tender status".format(tender.status)
        )
        request.errors.status = 403
        raise error_handler(request)


def validate_contract(request, **kwargs):
    contract = request.validated["contract"]
    if contract.status != "active":
        request.errors.add(
            "body", "data", "Can't update credentials in current ({}) contract status".format(contract.status)
        )
        request.errors.status = 403
        raise error_handler(request)


def validate_plan(request, **kwargs):
    plan = request.validated["plan"]
    if plan.status != "scheduled":
        request.errors.add(
            "body", "data", "Can't update credentials in current ({}) plan status".format(plan.status)
        )
        request.errors.status = 403
        raise error_handler(request)


def validate_agreement(request, **kwargs):
    agreement = request.validated["agreement"]
    if agreement.status != "active":
        request.errors.add(
            "body", "data", "Can't update credentials in current ({}) agreement status".format(agreement.status)
        )
        request.errors.status = 403
        raise error_handler(request)
