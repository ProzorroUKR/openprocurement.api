from openprocurement.api.utils import json_view
from openprocurement.tender.core.procedure.views.award import TenderAwardResource
from openprocurement.tender.belowthreshold.procedure.models.award import PatchAward, Award
from openprocurement.tender.belowthreshold.procedure.state.award import AwardState
from openprocurement.tender.core.procedure.validation import (
    validate_update_award_in_not_allowed_status,
    validate_update_award_only_for_active_lots,
    validate_update_award_status_before_milestone_due_date,
)
from openprocurement.tender.core.procedure.validation import (
    unless_admins,
    validate_item_owner,
    validate_input_data,
    validate_patch_data,
)
from cornice.resource import resource
from logging import getLogger

LOGGER = getLogger(__name__)


@resource(
    name="belowThreshold:Tender Awards",
    collection_path="/tenders/{tender_id}/awards",
    path="/tenders/{tender_id}/awards/{award_id}",
    description="Tender awards",
    procurementMethodType="belowThreshold",
)
class BelowThresholdTenderAwardResource(TenderAwardResource):
    state_class = AwardState

    @json_view(
        content_type="application/json",
        permission="edit_award",  # brokers
        validators=(
            unless_admins(
                validate_item_owner("tender"),
            ),
            validate_input_data(PatchAward),
            validate_patch_data(Award, item_name="award"),
            validate_update_award_in_not_allowed_status,
            validate_update_award_only_for_active_lots,
            validate_update_award_status_before_milestone_due_date,
        ),
    )
    def patch(self):
        return super().patch()
