from openprocurement.tender.core.procedure.views.award_milestone import BaseAwardMilestoneResource
from cornice.resource import resource


@resource(
    name="simple.defense:Tender Award Milestones",
    collection_path="/tenders/{tender_id}/awards/{award_id}/milestones",
    path="/tenders/{tender_id}/awards/{award_id}/milestones/{milestone_id}",
    description="Tender award milestones",
    procurementMethodType="simple.defense",
)
class CDStage2UAAwardMilestoneResource(BaseAwardMilestoneResource):
    pass
