from cornice.resource import resource

from openprocurement.api.constants import ProcurementMethodType
from openprocurement.tender.core.procedure.views.criterion_rg import BaseRequirementGroupResource
from openprocurement.tender.open.constants import OPEN_ROUTE_PREFIX
from openprocurement.tender.open.procedure.state.criterion_rg import (
    AboveThresholdEURequirementGroupState,
    AboveThresholdRequirementGroupState,
    AboveThresholdUARequirementGroupState,
    BelowThresholdRequirementGroupState,
    COLongRequirementGroupState,
    COShortRequirementGroupState,
    OpenTenderingEURequirementGroupState,
    OpenTenderingUARequirementGroupState,
    RFPRequirementGroupState,
    SimpleDefenseRequirementGroupState,
)
from openprocurement.tender.open.procedure.views.base import (
    COStateClass,
    OpenTenderingStateClass,
)


@resource(
    name=f"{OPEN_ROUTE_PREFIX}:Criteria Requirement Group",
    collection_path="/tenders/{tender_id}/criteria/{criterion_id}/requirement_groups",
    path="/tenders/{tender_id}/criteria/{criterion_id}/requirement_groups/{requirement_group_id}",
    description="Tender criteria requirement group",
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
class OpenBaseRequirementGroupResource(BaseRequirementGroupResource):
    state_classes = {
        ProcurementMethodType.ABOVE_THRESHOLD: AboveThresholdRequirementGroupState,
        ProcurementMethodType.ABOVE_THRESHOLD_UA: AboveThresholdUARequirementGroupState,
        ProcurementMethodType.ABOVE_THRESHOLD_EU: AboveThresholdEURequirementGroupState,
        ProcurementMethodType.OPEN_TENDERING: OpenTenderingStateClass(
            OpenTenderingUARequirementGroupState, OpenTenderingEURequirementGroupState
        ),
        ProcurementMethodType.SIMPLE_DEFENSE: SimpleDefenseRequirementGroupState,
        ProcurementMethodType.COMPETITIVE_ORDERING: COStateClass(
            COShortRequirementGroupState, COLongRequirementGroupState
        ),
        ProcurementMethodType.BELOW_THRESHOLD: BelowThresholdRequirementGroupState,
        ProcurementMethodType.REQUEST_FOR_PROPOSAL: RFPRequirementGroupState,
    }
