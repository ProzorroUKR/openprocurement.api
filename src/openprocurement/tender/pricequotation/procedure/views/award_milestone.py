from cornice.resource import resource

from openprocurement.tender.core.procedure.state.award_milestone import (
    AwardExtensionMilestoneState,
)
from openprocurement.tender.core.procedure.views.award_milestone import (
    BaseAwardMilestoneResource,
)
from openprocurement.tender.pricequotation.constants import PQ


@resource(
    name=f"{PQ}:Tender Award Milestones",
    collection_path="/tenders/{tender_id}/awards/{award_id}/milestones",
    path="/tenders/{tender_id}/awards/{award_id}/milestones/{milestone_id}",
    description="Tender award milestones",
    procurementMethodType=PQ,
)
class PQMilestoneResource(BaseAwardMilestoneResource):
    state_class = AwardExtensionMilestoneState
