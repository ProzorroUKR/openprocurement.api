from openprocurement.tender.core.procedure.views.award_milestone import BaseAwardMilestoneResource
from cornice.resource import resource


@resource(
    name="aboveThresholdUA:Tender Award Milestones",
    collection_path="/tenders/{tender_id}/awards/{award_id}/milestones",
    path="/tenders/{tender_id}/awards/{award_id}/milestones/{milestone_id}",
    description="Tender award milestones",
    procurementMethodType="aboveThresholdUA",
)
class UAAwardMilestoneResource(BaseAwardMilestoneResource):
    pass
