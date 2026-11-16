from cornice.resource import resource

from openprocurement.api.constants import ProcurementMethodType
from openprocurement.tender.core.procedure.views.criterion_rg_requirement import BaseRequirementResource
from openprocurement.tender.open.constants import OPEN_ROUTE_PREFIX
from openprocurement.tender.open.procedure.state.criterion_rg_requirement import (
    AboveThresholdEURequirementState,
    AboveThresholdRequirementState,
    AboveThresholdUARequirementState,
    BelowThresholdRequirementState,
    COLongRequirementState,
    COShortRequirementState,
    OpenTenderingEURequirementState,
    OpenTenderingUARequirementState,
    RFPRequirementState,
    SimpleDefenseRequirementState,
)
from openprocurement.tender.open.procedure.views.base import (
    COStateClass,
    OpenTenderingStateClass,
)


@resource(
    name=f"{OPEN_ROUTE_PREFIX}:Requirement Group Requirement",
    collection_path="/tenders/{tender_id}/criteria/{criterion_id}/requirement_groups/{requirement_group_id}/requirements",
    path="/tenders/{tender_id}/criteria/{criterion_id}/requirement_groups/{requirement_group_id}/requirements/{requirement_id}",
    description="Tender requirement group requirement",
    procurementMethodType=[
        ProcurementMethodType.ABOVE_THRESHOLD,
        ProcurementMethodType.ABOVE_THRESHOLD_UA,
        ProcurementMethodType.ABOVE_THRESHOLD_EU,
        ProcurementMethodType.OPEN_TENDERING,
        ProcurementMethodType.SIMPLE_DEFENSE,
        ProcurementMethodType.COMPETITIVE_ORDERING,
        ProcurementMethodType.BELOW_THRESHOLD,
        ProcurementMethodType.REQUEST_FOR_PROPOSAL,
    ],
)
class OpenBaseRequirementResource(BaseRequirementResource):
    state_classes = {
        ProcurementMethodType.ABOVE_THRESHOLD: AboveThresholdRequirementState,
        ProcurementMethodType.ABOVE_THRESHOLD_UA: AboveThresholdUARequirementState,
        ProcurementMethodType.ABOVE_THRESHOLD_EU: AboveThresholdEURequirementState,
        ProcurementMethodType.OPEN_TENDERING: OpenTenderingStateClass(
            OpenTenderingUARequirementState, OpenTenderingEURequirementState
        ),
        ProcurementMethodType.SIMPLE_DEFENSE: SimpleDefenseRequirementState,
        ProcurementMethodType.COMPETITIVE_ORDERING: COStateClass(COShortRequirementState, COLongRequirementState),
        ProcurementMethodType.BELOW_THRESHOLD: BelowThresholdRequirementState,
        ProcurementMethodType.REQUEST_FOR_PROPOSAL: RFPRequirementState,
    }
