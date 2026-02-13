from cornice.resource import resource

from openprocurement.api.procedure.validation import (
    validate_input_data,
    validate_item_owner,
)
from openprocurement.api.utils import json_view
from openprocurement.tender.arma.constants import COMPLEX_ASSET_ARMA
from openprocurement.tender.arma.procedure.models.award_milestone import (
    PostAwardMilestone,
)
from openprocurement.tender.core.procedure.state.award_milestone import (
    AwardExtensionMilestoneState,
)
from openprocurement.tender.core.procedure.validation import (
    validate_24h_milestone_released,
    validate_update_award_in_not_allowed_status,
    validate_update_award_only_for_active_lots,
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

    @json_view(
        content_type="application/json",
        permission="edit_tender",
        validators=(
            validate_item_owner("tender"),
            validate_24h_milestone_released,
            validate_input_data(PostAwardMilestone),
            validate_update_award_in_not_allowed_status,
            validate_update_award_only_for_active_lots,
        ),
    )
    def collection_post(self):
        return super().collection_post()
