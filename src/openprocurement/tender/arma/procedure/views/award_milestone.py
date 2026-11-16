from cornice.resource import resource

from openprocurement.api.constants import ProcurementMethodType
from openprocurement.tender.arma.procedure.state.award_milestone import ARMAAwardMilestoneState
from openprocurement.tender.core.procedure.views.award_milestone import (
    BaseAwardMilestoneResource,
)


@resource(
    name=f"{ProcurementMethodType.COMPLEX_ASSET_ARMA}:Tender Award Milestones",
    collection_path="/tenders/{tender_id}/awards/{award_id}/milestones",
    path="/tenders/{tender_id}/awards/{award_id}/milestones/{milestone_id}",
    description="Tender award milestones",
    procurementMethodType=ProcurementMethodType.COMPLEX_ASSET_ARMA,
)
class AwardMilestoneResource(BaseAwardMilestoneResource):
    state_class = ARMAAwardMilestoneState
