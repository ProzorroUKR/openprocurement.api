from cornice.resource import resource

from openprocurement.api.procedure.validation import (
    unless_admins,
    validate_input_data,
    validate_item_owner,
    validate_patch_data_simple,
    validate_patch_input_data,
)
from openprocurement.api.utils import json_view
from openprocurement.tender.arma.constants import COMPLEX_ASSET_ARMA
from openprocurement.tender.arma.procedure.models.award import ARMAAward, ARMAPostAward
from openprocurement.tender.arma.procedure.state.award import AwardState
from openprocurement.tender.core.procedure.models.award import PatchAward
from openprocurement.tender.core.procedure.validation import (
    validate_award_with_lot_cancellation_in_pending,
    validate_create_award_not_in_allowed_period,
    validate_update_award_in_not_allowed_status,
    validate_update_award_only_for_active_lots,
)
from openprocurement.tender.core.procedure.views.award import TenderAwardResource


@resource(
    name=f"{COMPLEX_ASSET_ARMA}:Tender Awards",
    collection_path="/tenders/{tender_id}/awards",
    path="/tenders/{tender_id}/awards/{award_id}",
    description="Tender awards",
    procurementMethodType=COMPLEX_ASSET_ARMA,
)
class AwardResource(TenderAwardResource):
    state_class = AwardState

    @json_view(
        content_type="application/json",
        permission="create_award",  # admins only
        validators=(
            validate_input_data(ARMAPostAward),
            validate_create_award_not_in_allowed_period,
        ),
    )
    def collection_post(self):
        return super().collection_post()

    @json_view(
        content_type="application/json",
        permission="edit_award",  # brokers
        validators=(
            unless_admins(validate_item_owner("tender")),
            validate_patch_input_data(PatchAward),
            validate_patch_data_simple(ARMAAward, item_name="award"),
            validate_award_with_lot_cancellation_in_pending,
            validate_update_award_in_not_allowed_status,
            validate_update_award_only_for_active_lots,
        ),
    )
    def patch(self):
        return super().patch()
