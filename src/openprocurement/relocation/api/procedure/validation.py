from hashlib import sha512

from openprocurement.api.auth import ACCR_1, ACCR_3, ACCR_5
from openprocurement.api.procedure.validation import validate_accreditation_level
from openprocurement.api.utils import error_handler
from openprocurement.api.validation import (
    validate_accreditation_level_owner,
    validate_json_data,
)
from openprocurement.tender.belowthreshold.procedure.state.tender_details import (
    BelowThresholdTenderDetailsState,
)
from openprocurement.tender.cfaselectionua.procedure.state.tender_details import (
    CFASelectionTenderDetailsState,
)
from openprocurement.tender.cfaua.procedure.state.tender_details import (
    CFAUATenderDetailsState,
)
from openprocurement.tender.competitivedialogue.procedure.state.stage1.tender_details import (
    CDEUStage1TenderDetailsState,
    CDUAStage1TenderDetailsState,
)
from openprocurement.tender.competitivedialogue.procedure.state.stage2.tender_details import (
    CDEUStage2TenderDetailsState,
    CDUAStage2TenderDetailsState,
)
from openprocurement.tender.esco.procedure.state.tender_details import (
    ESCOTenderDetailsState,
)
from openprocurement.tender.limited.procedure.state.tender_details import (
    NegotiationTenderDetailsState,
    ReportingTenderDetailsState,
)
from openprocurement.tender.open.procedure.state.tender_details import (
    OpenTenderDetailsState,
)
from openprocurement.tender.openeu.procedure.state.tender_details import (
    OpenEUTenderDetailsState,
)
from openprocurement.tender.openua.procedure.state.tender_details import (
    OpenUATenderDetailsState,
)
from openprocurement.tender.openuadefense.procedure.state.tender_details import (
    DefenseTenderDetailsState,
)
from openprocurement.tender.simpledefense.procedure.state.tender_details import (
    SimpleDefenseTenderDetailsState,
)


def validate_ownership_data(request, **kwargs):
    data = validate_json_data(request)
    for field in ["id", "transfer"]:
        if not data.get(field):
            request.errors.add("body", field, "This field is required.")
    if request.errors:
        request.errors.status = 422
        raise error_handler(request)
    request.validated["ownership_data"] = data


def validate_tender_transfer_accreditation_level(request, **kwargs):
    state_mapping = {
        "belowThreshold": BelowThresholdTenderDetailsState,
        "aboveThreshold": OpenTenderDetailsState,
        "aboveThresholdUA": OpenUATenderDetailsState,
        "aboveThresholdEU": OpenEUTenderDetailsState,
        "negotiation": NegotiationTenderDetailsState,
        "negotiation.quick": NegotiationTenderDetailsState,
        "aboveThresholdUA.defense": DefenseTenderDetailsState,
        "competitiveDialogueUA": CDUAStage1TenderDetailsState,
        "competitiveDialogueEU": CDEUStage1TenderDetailsState,
        "competitiveDialogueUA.stage2": CDUAStage2TenderDetailsState,
        "competitiveDialogueEU.stage2": CDEUStage2TenderDetailsState,
        "reporting": ReportingTenderDetailsState,
        "esco": ESCOTenderDetailsState,
        "closeFrameworkAgreementUA": CFAUATenderDetailsState,
        "closeFrameworkAgreementSelectionUA": CFASelectionTenderDetailsState,
        "priceQuotation": None,
        "simple.defense": SimpleDefenseTenderDetailsState,
    }
    state = state_mapping.get(request.validated["tender"]["procurementMethodType"], None)
    if state is None:
        raise NotImplementedError()

    if hasattr(state, "tender_transfer_accreditations"):
        levels = state.tender_transfer_accreditations
    elif hasattr(state, "tender_create_accreditations"):
        levels = state.tender_create_accreditations
    else:
        levels = None

    if levels is None:
        raise NotImplementedError()

    if hasattr(state, "tender_central_accreditations"):
        kind_central_levels = state.tender_central_accreditations
    else:
        kind_central_levels = None

    validate_accreditation_level(
        levels=levels,
        item="ownership",
        operation="change",
        source="tender",
        kind_central_levels=kind_central_levels,
    )(request, **kwargs)


def validate_contract_transfer_accreditation_level(request, **kwargs):
    validate_accreditation_level(
        levels=(ACCR_3, ACCR_5),
        item="ownership",
        operation="change",
        source="contract",
    )(request, **kwargs)


def validate_plan_transfer_accreditation_level(request, **kwargs):
    validate_accreditation_level(
        levels=(ACCR_1, ACCR_3, ACCR_5),
        item="ownership",
        operation="change",
        source="plan",
    )(request, **kwargs)


def validate_agreement_transfer_accreditation_level(request, **kwargs):
    validate_accreditation_level(
        levels=(ACCR_3, ACCR_5),
        item="ownership",
        operation="change",
        source="agreement",
    )(request, **kwargs)


def validate_owner_accreditation_level(request, obj):
    validate_accreditation_level_owner(request, obj["owner"], "ownership", "ownership", "change")


def validate_tender_owner_accreditation_level(request, **kwargs):
    validate_owner_accreditation_level(request, request.validated["tender"])


def validate_plan_owner_accreditation_level(request, **kwargs):
    validate_owner_accreditation_level(request, request.validated["plan"])


def validate_contract_owner_accreditation_level(request, **kwargs):
    validate_owner_accreditation_level(request, request.validated["contract"])


def validate_agreement_owner_accreditation_level(request, **kwargs):
    validate_owner_accreditation_level(request, request.validated["agreement"])


def validate_tender(request, **kwargs):
    tender = request.validated["tender"]
    if tender["status"] in [
        "complete",
        "unsuccessful",
        "cancelled",
        "active.stage2.waiting",
        "draft.pending",
        "draft.unsuccessful",
    ]:
        request.errors.add(
            "body",
            "data",
            "Can't update credentials in current ({}) tender status".format(tender["status"]),
        )
        request.errors.status = 403
        raise error_handler(request)


def validate_plan(request, **kwargs):
    plan = request.validated["plan"]
    if plan["status"] != "scheduled":
        request.errors.add(
            "body",
            "data",
            "Can't update credentials in current ({}) plan status".format(plan["status"]),
        )
        request.errors.status = 403
        raise error_handler(request)


def validate_contract(request, **kwargs):
    contract = request.validated["contract"]
    if contract["status"] not in ("pending", "active"):
        request.errors.add(
            "body",
            "data",
            "Can't update credentials in current ({}) contract status".format(contract["status"]),
        )
        request.errors.status = 403
        raise error_handler(request)


def validate_agreement(request, **kwargs):
    agreement = request.validated["agreement"]
    if agreement["status"] != "active":
        request.errors.add(
            "body",
            "data",
            "Can't update credentials in current ({}) agreement status".format(agreement["status"]),
        )
        request.errors.status = 403
        raise error_handler(request)


def validate_transfer_token(request, obj):
    token = request.validated["ownership_data"]["transfer"]
    if obj["transfer_token"] != sha512(token.encode("utf-8")).hexdigest():
        request.errors.add("body", "transfer", "Invalid transfer")
        request.errors.status = 403
        raise error_handler(request)


def validate_tender_transfer_token(request, **kwargs):
    validate_transfer_token(request, request.validated["tender"])


def validate_plan_transfer_token(request, **kwargs):
    validate_transfer_token(request, request.validated["plan"])


def validate_contract_transfer_token(request, **kwargs):
    validate_transfer_token(request, request.validated["contract"])


def validate_agreement_transfer_token(request, **kwargs):
    validate_transfer_token(request, request.validated["agreement"])
