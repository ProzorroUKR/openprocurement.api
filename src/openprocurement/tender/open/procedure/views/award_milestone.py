from cornice.resource import resource

from openprocurement.tender.core.procedure.state.award_milestone import (
    AwardExtensionMilestoneState,
    AwardMilestoneState,
)
from openprocurement.tender.core.procedure.views.award_milestone import BaseAwardMilestoneResource
from openprocurement.tender.open.constants import (
    ABOVE_THRESHOLD,
    ABOVE_THRESHOLD_EU,
    ABOVE_THRESHOLD_UA,
    ABOVE_THRESHOLD_UA_DEFENSE,
    BELOW_THRESHOLD,
    COMPETITIVE_ORDERING,
    OPEN_PROCUREMENT_METHOD_TYPES,
    OPEN_ROUTE_PREFIX,
    REQUEST_FOR_PROPOSAL,
    SIMPLE_DEFENSE,
)
from openprocurement.tender.open.procedure.state.award_milestone import (
    BelowThresholdAwardMilestoneState,
    RFPAwardMilestoneState,
)


@resource(
    name=f"{OPEN_ROUTE_PREFIX}:Tender Award Milestones",
    collection_path="/tenders/{tender_id}/awards/{award_id}/milestones",
    path="/tenders/{tender_id}/awards/{award_id}/milestones/{milestone_id}",
    description="Tender award milestones",
    procurementMethodType=OPEN_PROCUREMENT_METHOD_TYPES,
)
class OpenBaseAwardMilestoneResource(BaseAwardMilestoneResource):
    state_classes = {
        ABOVE_THRESHOLD: AwardMilestoneState,
        ABOVE_THRESHOLD_UA: AwardMilestoneState,
        ABOVE_THRESHOLD_EU: AwardExtensionMilestoneState,
        ABOVE_THRESHOLD_UA_DEFENSE: AwardMilestoneState,
        SIMPLE_DEFENSE: AwardMilestoneState,
        COMPETITIVE_ORDERING: AwardMilestoneState,
        BELOW_THRESHOLD: BelowThresholdAwardMilestoneState,
        REQUEST_FOR_PROPOSAL: RFPAwardMilestoneState,
    }
