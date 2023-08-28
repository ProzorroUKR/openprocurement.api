from openprocurement.tender.core.procedure.views.award_milestone import BaseAwardMilestoneResource
from cornice.resource import resource

from openprocurement.tender.open.constants import ABOVE_THRESHOLD_GROUP_NAME, ABOVE_THRESHOLD_GROUP


@resource(
    name=f"{ABOVE_THRESHOLD_GROUP_NAME}:Tender Award Milestones",
    collection_path="/tenders/{tender_id}/awards/{award_id}/milestones",
    path="/tenders/{tender_id}/awards/{award_id}/milestones/{milestone_id}",
    description="Tender award milestones",
    procurementMethodType=ABOVE_THRESHOLD_GROUP,
)
class UAAwardMilestoneResource(BaseAwardMilestoneResource):
    pass
