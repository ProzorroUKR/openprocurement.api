from cornice.resource import resource

from openprocurement.api.utils import json_view
from openprocurement.tender.core.procedure.views.lot import TenderLotResource
from openprocurement.tender.core.procedure.validation import (
    validate_item_owner,
    validate_input_data,
    validate_lot_operation_in_disallowed_tender_statuses,
    validate_create_award_only_for_active_lot,
    validate_operation_with_lot_cancellation_in_pending,
    validate_tender_period_extension,
    validate_delete_lot_related_object,
)
from openprocurement.tender.core.procedure.models.lot import PostLot
from openprocurement.tender.cfaua.procedure.state.lot import TenderLotState
from openprocurement.tender.cfaua.procedure.validation import validate_lot_count


@resource(
    name="closeFrameworkAgreementUA:Tender Lots",
    collection_path="/tenders/{tender_id}/lots",
    path="/tenders/{tender_id}/lots/{lot_id}",
    procurementMethodType="closeFrameworkAgreementUA",
    description="Tender EU lots",
)
class CFAUATenderLotResource(TenderLotResource):
    state_class = TenderLotState

    @json_view(
        content_type="application/json",
        permission="create_lot",
        validators=(
            validate_item_owner("tender"),
            validate_lot_operation_in_disallowed_tender_statuses,
            validate_input_data(PostLot),
            validate_lot_count,
            validate_create_award_only_for_active_lot,
        ),
    )
    def collection_post(self):
        return super().collection_post()

    @json_view(
        permission="edit_lot",
        validators=(
            validate_item_owner("tender"),
            validate_lot_operation_in_disallowed_tender_statuses,
            validate_operation_with_lot_cancellation_in_pending("lot"),
            validate_delete_lot_related_object,
            validate_tender_period_extension,
            validate_lot_count,
        ),
    )
    def delete(self):
        return super().delete()
