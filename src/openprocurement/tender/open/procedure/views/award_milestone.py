from openprocurement.tender.core.procedure.views.award_milestone import BaseAwardMilestoneResource
from cornice.resource import resource

from openprocurement.tender.open.constants import ABOVE_THRESHOLD


@resource(
    name=f"{ABOVE_THRESHOLD}:Tender Award Milestones",
    collection_path="/tenders/{tender_id}/awards/{award_id}/milestones",
    path="/tenders/{tender_id}/awards/{award_id}/milestones/{milestone_id}",
    description="Tender award milestones",
    procurementMethodType=ABOVE_THRESHOLD,
)
class UAAwardMilestoneResource(BaseAwardMilestoneResource):
    pass
