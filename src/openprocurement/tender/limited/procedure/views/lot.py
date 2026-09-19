from typing import Optional

from cornice.resource import resource

from openprocurement.api.procedure.validation import (
    validate_input_data,
    validate_item_owner,
    validate_patch_data_simple,
    validate_patch_input_data,
)
from openprocurement.api.utils import json_view
from openprocurement.tender.core.procedure.validation import (
    validate_limited_lot_operation_in_disallowed_tender_statuses,
)
from openprocurement.tender.core.procedure.views.lot import TenderLotResource
from openprocurement.tender.limited.procedure.models.lot import LimitedLot, LimitedPatchLot, LimitedPostLot
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
            validate_input_data(LimitedPostLot),
            validate_limited_lot_operation_in_disallowed_tender_statuses,
        ),
    )
    def collection_post(self) -> Optional[dict]:
        return super().collection_post()

    @json_view(
        content_type="application/json",
        validators=(
            validate_item_owner("tender"),
            validate_limited_lot_operation_in_disallowed_tender_statuses,
            validate_patch_input_data(LimitedPatchLot),
            validate_patch_data_simple(LimitedLot, item_name="lot"),
        ),
        permission="edit_lot",
    )
    def patch(self) -> Optional[dict]:
        return super().patch()

    @json_view(
        content_type="application/json",
        validators=(
            validate_item_owner("tender"),
            validate_limited_lot_operation_in_disallowed_tender_statuses,
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
