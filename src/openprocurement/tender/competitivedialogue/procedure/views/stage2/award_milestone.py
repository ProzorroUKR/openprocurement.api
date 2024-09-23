from cornice.resource import resource

from openprocurement.tender.competitivedialogue.constants import (
    STAGE_2_EU_TYPE,
    STAGE_2_UA_TYPE,
)
from openprocurement.tender.core.procedure.state.award_milestone import (
    AwardExtensionMilestoneState,
)
from openprocurement.tender.core.procedure.views.award_milestone import (
    BaseAwardMilestoneResource,
)


@resource(
    name="{}:Tender Award Milestones".format(STAGE_2_UA_TYPE),
    collection_path="/tenders/{tender_id}/awards/{award_id}/milestones",
    path="/tenders/{tender_id}/awards/{award_id}/milestones/{milestone_id}",
    description="Tender award milestones",
    procurementMethodType=STAGE_2_UA_TYPE,
)
class CDStage2UAAwardMilestoneResource(BaseAwardMilestoneResource):
    pass


@resource(
    name="{}:Tender Award Milestones".format(STAGE_2_EU_TYPE),
    collection_path="/tenders/{tender_id}/awards/{award_id}/milestones",
    path="/tenders/{tender_id}/awards/{award_id}/milestones/{milestone_id}",
    description="Tender award milestones",
    procurementMethodType=STAGE_2_EU_TYPE,
)
class CDStage2EUAwardMilestoneResource(BaseAwardMilestoneResource):
    state_class = AwardExtensionMilestoneState
