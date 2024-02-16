from typing import Optional

from cornice.resource import resource

from openprocurement.api.procedure.validation import (
    validate_input_data,
    validate_patch_data_simple,
)
from openprocurement.api.utils import json_view
from openprocurement.tender.core.procedure.validation import (
    validate_lot_operation_in_disallowed_tender_statuses,
    validate_operation_with_lot_cancellation_in_pending,
)
from openprocurement.tender.core.procedure.views.lot import TenderLotResource
from openprocurement.tender.esco.procedure.models.lot import Lot, PatchLot, PostLot
from openprocurement.tender.esco.procedure.state.lot import TenderLotState


@resource(
    name="esco:Tender Lots",
    collection_path="/tenders/{tender_id}/lots",
    path="/tenders/{tender_id}/lots/{lot_id}",
    procurementMethodType="esco",
    description="Tender ESCO lots",
)
class ESCOLotResource(TenderLotResource):
    state_class = TenderLotState

    @json_view(
        content_type="application/json",
        permission="create_lot",
        validators=(
            validate_lot_operation_in_disallowed_tender_statuses,
            validate_input_data(PostLot),
        ),
    )
    def collection_post(self) -> Optional[dict]:
        return super().collection_post()

    @json_view(
        content_type="application/json",
        validators=(
            validate_lot_operation_in_disallowed_tender_statuses,
            validate_input_data(PatchLot),
            validate_patch_data_simple(Lot, item_name="lot"),
            validate_operation_with_lot_cancellation_in_pending("lot"),
        ),
        permission="edit_lot",
    )
    def patch(self) -> Optional[dict]:
        return super().patch()
