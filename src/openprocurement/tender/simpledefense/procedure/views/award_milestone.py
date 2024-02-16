from cornice.resource import resource

from openprocurement.tender.core.procedure.views.award_milestone import (
    BaseAwardMilestoneResource,
)


@resource(
    name="simple.defense:Tender Award Milestones",
    collection_path="/tenders/{tender_id}/awards/{award_id}/milestones",
    path="/tenders/{tender_id}/awards/{award_id}/milestones/{milestone_id}",
    description="Tender award milestones",
    procurementMethodType="simple.defense",
)
class SimpleDefenseAwardMilestoneResource(BaseAwardMilestoneResource):
    pass
