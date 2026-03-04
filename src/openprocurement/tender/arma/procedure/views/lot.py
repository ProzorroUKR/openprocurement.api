from typing import Optional

from cornice.resource import resource

from openprocurement.api.procedure.validation import (
    validate_input_data,
    validate_item_owner,
    validate_patch_data_simple,
)
from openprocurement.api.utils import json_view
from openprocurement.tender.arma.constants import COMPLEX_ASSET_ARMA
from openprocurement.tender.arma.procedure.models.lot import Lot, PatchLot, PostLot
from openprocurement.tender.arma.procedure.state.lot import LotState
from openprocurement.tender.core.procedure.validation import (
    validate_lot_operation_in_disallowed_tender_statuses,
    validate_operation_with_lot_cancellation_in_pending,
)
from openprocurement.tender.core.procedure.views.lot import TenderLotResource


@resource(
    name=f"{COMPLEX_ASSET_ARMA}:Tender Lots",
    collection_path="/tenders/{tender_id}/lots",
    path="/tenders/{tender_id}/lots/{lot_id}",
    procurementMethodType=COMPLEX_ASSET_ARMA,
    description="ARMA lots",
)
class LotResource(TenderLotResource):
    state_class = LotState

    @json_view(
        content_type="application/json",
        permission="create_lot",
        validators=(
            validate_item_owner("tender"),
            validate_lot_operation_in_disallowed_tender_statuses,
            validate_input_data(PostLot),
        ),
    )
    def collection_post(self) -> Optional[dict]:
        return super().collection_post()

    @json_view(
        content_type="application/json",
        validators=(
            validate_item_owner("tender"),
            validate_lot_operation_in_disallowed_tender_statuses,
            validate_input_data(PatchLot),
            validate_patch_data_simple(Lot, item_name="lot"),
            validate_operation_with_lot_cancellation_in_pending("lot"),
        ),
        permission="edit_lot",
    )
    def patch(self) -> Optional[dict]:
        return super().patch()
