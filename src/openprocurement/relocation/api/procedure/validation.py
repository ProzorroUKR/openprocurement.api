from hashlib import sha512

from openprocurement.api.auth import AccreditationLevel
from openprocurement.api.constants import ProcurementMethodType
from openprocurement.api.procedure.validation import validate_accreditation_level
from openprocurement.api.utils import error_handler
from openprocurement.api.validation import (
    validate_accreditation_level_owner,
    validate_json_data,
)
from openprocurement.tender.cfaselectionua.procedure.state.tender_details import (
    CFASelectionTenderDetailsState,
)
from openprocurement.tender.cfaua.procedure.state.tender_details import (
    CFAUATenderDetailsState,
)
from openprocurement.tender.competitivedialogue.procedure.state.stage1.tender_details import (
    CDStage1EUTenderDetailsState,
    CDStage1UATenderDetailsState,
)
from openprocurement.tender.competitivedialogue.procedure.state.stage2.tender_details import (
    CDStage2EUTenderDetailsState,
    CDStage2UATenderDetailsState,
)
from openprocurement.tender.esco.procedure.state.tender_details import (
    ESCOTenderDetailsState,
)
from openprocurement.tender.limited.procedure.state.tender_details import (
    NegotiationTenderDetailsState,
    ReportingTenderDetailsState,
)
from openprocurement.tender.open.procedure.state.tender_details import (
    AboveThresholdEUTenderDetailsState,
    AboveThresholdTenderDetailsState,
    AboveThresholdUATenderDetailsState,
    BelowThresholdTenderDetailsState,
    DefenseTenderDetailsState,
    OpenTenderingTenderDetailsState,
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
        ProcurementMethodType.BELOW_THRESHOLD: BelowThresholdTenderDetailsState,
        ProcurementMethodType.ABOVE_THRESHOLD: AboveThresholdTenderDetailsState,
        ProcurementMethodType.ABOVE_THRESHOLD_UA: AboveThresholdUATenderDetailsState,
        ProcurementMethodType.ABOVE_THRESHOLD_EU: AboveThresholdEUTenderDetailsState,
        ProcurementMethodType.NEGOTIATION: NegotiationTenderDetailsState,
        ProcurementMethodType.NEGOTIATION_QUICK: NegotiationTenderDetailsState,
        ProcurementMethodType.ABOVE_THRESHOLD_UA_DEFENSE: DefenseTenderDetailsState,
        ProcurementMethodType.COMPETITIVE_DIALOGUE_UA: CDStage1UATenderDetailsState,
        ProcurementMethodType.COMPETITIVE_DIALOGUE_EU: CDStage1EUTenderDetailsState,
        ProcurementMethodType.COMPETITIVE_DIALOGUE_UA_STAGE2: CDStage2UATenderDetailsState,
        ProcurementMethodType.COMPETITIVE_DIALOGUE_EU_STAGE2: CDStage2EUTenderDetailsState,
        ProcurementMethodType.REPORTING: ReportingTenderDetailsState,
        ProcurementMethodType.ESCO: ESCOTenderDetailsState,
        ProcurementMethodType.CLOSE_FRAMEWORK_AGREEMENT_UA: CFAUATenderDetailsState,
        ProcurementMethodType.CLOSE_FRAMEWORK_AGREEMENT_SELECTION_UA: CFASelectionTenderDetailsState,
        ProcurementMethodType.PRICE_QUOTATION: None,
        ProcurementMethodType.SIMPLE_DEFENSE: SimpleDefenseTenderDetailsState,
        ProcurementMethodType.OPEN_TENDERING: OpenTenderingTenderDetailsState,
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
        levels=(AccreditationLevel.ACCR_3, AccreditationLevel.ACCR_5),
        item="ownership",
        operation="change",
        source="contract",
    )(request, **kwargs)


def validate_plan_transfer_accreditation_level(request, **kwargs):
    validate_accreditation_level(
        levels=(AccreditationLevel.ACCR_1, AccreditationLevel.ACCR_3, AccreditationLevel.ACCR_5),
        item="ownership",
        operation="change",
        source="plan",
    )(request, **kwargs)


def validate_agreement_transfer_accreditation_level(request, **kwargs):
    validate_accreditation_level(
        levels=(AccreditationLevel.ACCR_3, AccreditationLevel.ACCR_5),
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
