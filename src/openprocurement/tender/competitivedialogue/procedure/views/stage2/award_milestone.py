from openprocurement.tender.competitivedialogue.constants import STAGE_2_UA_TYPE
from openprocurement.tender.core.procedure.views.award_milestone import BaseAwardMilestoneResource
from cornice.resource import resource


@resource(
    name="{}:Tender Award Milestones".format(STAGE_2_UA_TYPE),
    collection_path="/tenders/{tender_id}/awards/{award_id}/milestones",
    path="/tenders/{tender_id}/awards/{award_id}/milestones/{milestone_id}",
    description="Tender award milestones",
    procurementMethodType=STAGE_2_UA_TYPE,
)
class CDStage2UAAwardMilestoneResource(BaseAwardMilestoneResource):
    pass
