from cornice.resource import resource

from openprocurement.api.procedure.validation import (
    unless_admins,
    validate_item_owner,
    validate_patch_data_simple,
    validate_patch_input_data,
)
from openprocurement.api.utils import json_view
from openprocurement.tender.core.procedure.models.award import Award, PatchAward
from openprocurement.tender.core.procedure.validation import (
    validate_award_with_lot_cancellation_in_pending,
    validate_update_award_in_not_allowed_status,
    validate_update_award_only_for_active_lots,
)
from openprocurement.tender.core.procedure.views.award import TenderAwardResource
from openprocurement.tender.open.constants import ABOVE_THRESHOLD
from openprocurement.tender.open.procedure.state.award import AwardState


@resource(
    name=f"{ABOVE_THRESHOLD}:Tender Awards",
    collection_path="/tenders/{tender_id}/awards",
    path="/tenders/{tender_id}/awards/{award_id}",
    description="Tender awards",
    procurementMethodType=ABOVE_THRESHOLD,
)
class UATenderAwardResource(TenderAwardResource):
    state_class = AwardState

    @json_view(
        content_type="application/json",
        permission="edit_award",  # brokers
        validators=(
            unless_admins(validate_item_owner("tender")),
            validate_patch_input_data(PatchAward),
            validate_patch_data_simple(Award, item_name="award"),
            validate_award_with_lot_cancellation_in_pending,
            validate_update_award_in_not_allowed_status,
            validate_update_award_only_for_active_lots,
        ),
    )
    def patch(self):
        return super().patch()
