from cornice.resource import resource

from openprocurement.tender.core.procedure.views.criterion_rg_requirement import BaseRequirementResource
from openprocurement.tender.open.constants import (
    ABOVE_THRESHOLD,
    ABOVE_THRESHOLD_EU,
    ABOVE_THRESHOLD_UA,
    BELOW_THRESHOLD,
    COMPETITIVE_ORDERING,
    OPEN_ROUTE_PREFIX,
    REQUEST_FOR_PROPOSAL,
    SIMPLE_DEFENSE,
)
from openprocurement.tender.open.procedure.state.criterion_rg_requirement import (
    AboveThresholdEURequirementState,
    AboveThresholdRequirementState,
    AboveThresholdUARequirementState,
    BelowThresholdRequirementState,
    COLongRequirementState,
    COShortRequirementState,
    RFPRequirementState,
)
from openprocurement.tender.open.procedure.views.base import COStateClass


@resource(
    name=f"{OPEN_ROUTE_PREFIX}:Requirement Group Requirement",
    collection_path="/tenders/{tender_id}/criteria/{criterion_id}/requirement_groups/{requirement_group_id}/requirements",
    path="/tenders/{tender_id}/criteria/{criterion_id}/requirement_groups/{requirement_group_id}/requirements/{requirement_id}",
    description="Tender requirement group requirement",
    procurementMethodType=[
        ABOVE_THRESHOLD,
        ABOVE_THRESHOLD_UA,
        ABOVE_THRESHOLD_EU,
        SIMPLE_DEFENSE,
        COMPETITIVE_ORDERING,
        BELOW_THRESHOLD,
        REQUEST_FOR_PROPOSAL,
    ],
)
class OpenBaseRequirementResource(BaseRequirementResource):
    state_classes = {
        ABOVE_THRESHOLD: AboveThresholdRequirementState,
        ABOVE_THRESHOLD_UA: AboveThresholdUARequirementState,
        ABOVE_THRESHOLD_EU: AboveThresholdEURequirementState,
        SIMPLE_DEFENSE: AboveThresholdUARequirementState,
        COMPETITIVE_ORDERING: COStateClass(COShortRequirementState, COLongRequirementState),
        BELOW_THRESHOLD: BelowThresholdRequirementState,
        REQUEST_FOR_PROPOSAL: RFPRequirementState,
    }
