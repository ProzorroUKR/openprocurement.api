from typing import Optional

from cornice.resource import resource

from openprocurement.api.utils import json_view
from openprocurement.tender.core.procedure.views.lot import TenderLotResource
from openprocurement.tender.core.procedure.validation import (
    validate_item_owner,
    validate_input_data,
    validate_patch_data_simple,
    validate_operation_with_lot_cancellation_in_pending,
    validate_delete_lot_related_object,
)
from openprocurement.tender.limited.procedure.validation import (
    validate_lot_operation_in_disallowed_tender_statuses,
    validate_lot_operation_with_awards,
)
from openprocurement.tender.limited.procedure.models.lot import PostLot, PatchLot, Lot
from openprocurement.tender.limited.procedure.state.lot import NegotiationLotState


@resource(
    name="negotiation.quick:Tender Lots",
    collection_path="/tenders/{tender_id}/lots",
    path="/tenders/{tender_id}/lots/{lot_id}",
    procurementMethodType="negotiation.quick",
    description="Tender limited negotiation quick lots",
)
class TenderLimitedNegotiationQuickLotResource(TenderLotResource):
    state_class = NegotiationLotState

    @json_view(
        content_type="application/json",
        permission="create_lot",
        validators=(
            validate_item_owner("tender"),
            validate_input_data(PostLot),
            validate_lot_operation_in_disallowed_tender_statuses,
            validate_lot_operation_with_awards,
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
            validate_lot_operation_with_awards,
        ),
        permission="edit_lot",
    )
    def patch(self) -> Optional[dict]:
        return super().patch()

    @json_view(
        content_type="application/json",
        validators=(
            validate_item_owner("tender"),
            validate_operation_with_lot_cancellation_in_pending("lot"),
            validate_lot_operation_in_disallowed_tender_statuses,
            validate_delete_lot_related_object,
            validate_lot_operation_with_awards,
        ),
        permission="edit_lot",
    )
    def delete(self) -> Optional[dict]:
        return super().delete()


@resource(
    name="negotiation:Tender Lots",
    collection_path="/tenders/{tender_id}/lots",
    path="/tenders/{tender_id}/lots/{lot_id}",
    procurementMethodType="negotiation",
    description="Tender limited negotiation lots",
)
class TenderLimitedNegotiationLotResource(TenderLimitedNegotiationQuickLotResource):
    pass
