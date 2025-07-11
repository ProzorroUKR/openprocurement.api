from cornice.resource import resource

from openprocurement.api.procedure.validation import (
    unless_admins,
    validate_input_data,
    validate_item_owner,
    validate_patch_data_simple,
)
from openprocurement.api.utils import json_view
from openprocurement.tender.competitiveordering.constants import COMPETITIVE_ORDERING
from openprocurement.tender.competitiveordering.procedure.models.award import (
    Award,
    PatchAward,
)
from openprocurement.tender.competitiveordering.procedure.state.award import (
    COAwardState,
)
from openprocurement.tender.core.procedure.validation import (
    validate_award_with_lot_cancellation_in_pending,
    validate_update_award_in_not_allowed_status,
    validate_update_award_only_for_active_lots,
    validate_update_award_status_before_milestone_due_date,
    validate_update_award_with_accepted_complaint,
)
from openprocurement.tender.core.procedure.views.award import TenderAwardResource


@resource(
    name=f"{COMPETITIVE_ORDERING}:Tender Awards",
    collection_path="/tenders/{tender_id}/awards",
    path="/tenders/{tender_id}/awards/{award_id}",
    description="Tender awards",
    procurementMethodType=COMPETITIVE_ORDERING,
)
class COTenderAwardResource(TenderAwardResource):
    state_class = COAwardState

    @json_view(
        content_type="application/json",
        permission="edit_award",  # brokers
        validators=(
            unless_admins(validate_item_owner("tender")),
            validate_input_data(
                PatchAward,
                none_means_remove=True,
            ),
            validate_patch_data_simple(Award, item_name="award"),
            validate_award_with_lot_cancellation_in_pending,
            validate_update_award_in_not_allowed_status,
            validate_update_award_only_for_active_lots,
            validate_update_award_with_accepted_complaint,
            validate_update_award_status_before_milestone_due_date,
        ),
    )
    def patch(self):
        return super().patch()
