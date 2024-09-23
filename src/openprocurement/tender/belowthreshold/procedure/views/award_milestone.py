from cornice.resource import resource

from openprocurement.tender.belowthreshold.procedure.state.award_milestone import (
    BelowThresholdAwardMilestoneState,
)
from openprocurement.tender.core.procedure.views.award_milestone import (
    BaseAwardMilestoneResource,
)


@resource(
    name="belowThreshold:Tender Award Milestones",
    collection_path="/tenders/{tender_id}/awards/{award_id}/milestones",
    path="/tenders/{tender_id}/awards/{award_id}/milestones/{milestone_id}",
    description="Tender award milestones",
    procurementMethodType="belowThreshold",
)
class BelowThresholdAwardMilestoneResource(BaseAwardMilestoneResource):
    state_class = BelowThresholdAwardMilestoneState
