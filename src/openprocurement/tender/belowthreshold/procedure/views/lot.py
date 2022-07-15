from typing import Optional

from cornice.resource import resource

from openprocurement.api.utils import json_view
from openprocurement.tender.core.procedure.views.lot import TenderLotResource
from openprocurement.tender.core.procedure.validation import (
    validate_item_owner,
    validate_input_data,
    validate_patch_data_simple,
    validate_delete_lot_related_object,
)
from openprocurement.tender.core.procedure.models.lot import PostLot, PatchLot, Lot
from openprocurement.tender.belowthreshold.procedure.state.lot import TenderLotState
from openprocurement.tender.belowthreshold.procedure.validation import (
    validate_lot_operation_in_disallowed_tender_statuses,
)


@resource(
    name="belowThreshold:Tender Lots",
    collection_path="/tenders/{tender_id}/lots",
    path="/tenders/{tender_id}/lots/{lot_id}",
    procurementMethodType="belowThreshold",
    description="Tender lots",
)
class BelowThresholdTenderLotResource(TenderLotResource):
    state_class = TenderLotState

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
        ),
        permission="edit_lot",
    )
    def patch(self) -> Optional[dict]:
        return super().patch()

    @json_view(
        content_type="application/json",
        validators=(
            validate_item_owner("tender"),
            validate_lot_operation_in_disallowed_tender_statuses,
            validate_delete_lot_related_object,
        ),
        permission="edit_lot",
    )
    def delete(self) -> Optional[dict]:
        return super().delete()
