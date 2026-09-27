from cornice.resource import resource

from openprocurement.tender.core.procedure.views.criterion_rg import BaseRequirementGroupResource
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
from openprocurement.tender.open.procedure.state.criterion_rg import (
    AboveThresholdEURequirementGroupState,
    AboveThresholdRequirementGroupState,
    AboveThresholdUARequirementGroupState,
    BelowThresholdRequirementGroupState,
    COLongRequirementGroupState,
    COShortRequirementGroupState,
    RFPRequirementGroupState,
)
from openprocurement.tender.open.procedure.views.base import COStateResourceMixin


@resource(
    name=f"{OPEN_ROUTE_PREFIX}:Criteria Requirement Group",
    collection_path="/tenders/{tender_id}/criteria/{criterion_id}/requirement_groups",
    path="/tenders/{tender_id}/criteria/{criterion_id}/requirement_groups/{requirement_group_id}",
    description="Tender criteria requirement group",
    procurementMethodType=[
        ABOVE_THRESHOLD,
        ABOVE_THRESHOLD_UA,
        ABOVE_THRESHOLD_EU,
        SIMPLE_DEFENSE,
        BELOW_THRESHOLD,
        REQUEST_FOR_PROPOSAL,
    ],
)
class OpenBaseRequirementGroupResource(BaseRequirementGroupResource):
    state_classes = {
        ABOVE_THRESHOLD: AboveThresholdRequirementGroupState,
        ABOVE_THRESHOLD_UA: AboveThresholdUARequirementGroupState,
        ABOVE_THRESHOLD_EU: AboveThresholdEURequirementGroupState,
        SIMPLE_DEFENSE: AboveThresholdUARequirementGroupState,
        BELOW_THRESHOLD: BelowThresholdRequirementGroupState,
        REQUEST_FOR_PROPOSAL: RFPRequirementGroupState,
    }


@resource(
    name=f"{OPEN_ROUTE_PREFIX}:Criteria Requirement Group (competitiveOrdering)",
    collection_path="/tenders/{tender_id}/criteria/{criterion_id}/requirement_groups",
    path="/tenders/{tender_id}/criteria/{criterion_id}/requirement_groups/{requirement_group_id}",
    description="Tender criteria requirement group",
    procurementMethodType=COMPETITIVE_ORDERING,
)
class CORequirementGroupResource(COStateResourceMixin, BaseRequirementGroupResource):
    state_short_class = COShortRequirementGroupState
    state_long_class = COLongRequirementGroupState
