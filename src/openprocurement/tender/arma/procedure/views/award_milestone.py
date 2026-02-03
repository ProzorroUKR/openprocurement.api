from cornice.resource import resource

from openprocurement.tender.arma.constants import COMPLEX_ASSET_ARMA
from openprocurement.tender.core.procedure.state.award_milestone import (
    AwardExtensionMilestoneState,
)
from openprocurement.tender.core.procedure.views.award_milestone import (
    BaseAwardMilestoneResource,
)


@resource(
    name="complexAsset.arma:Tender Award Milestones",
    collection_path="/tenders/{tender_id}/awards/{award_id}/milestones",
    path="/tenders/{tender_id}/awards/{award_id}/milestones/{milestone_id}",
    description="Tender award milestones",
    procurementMethodType=COMPLEX_ASSET_ARMA,
)
class AwardMilestoneResource(BaseAwardMilestoneResource):
    state_class = AwardExtensionMilestoneState
