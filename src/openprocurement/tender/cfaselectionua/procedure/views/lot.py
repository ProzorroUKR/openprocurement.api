from typing import Optional

from cornice.resource import resource

from openprocurement.api.procedure.validation import (
    validate_input_data,
    validate_item_owner,
    validate_patch_data_simple,
)
from openprocurement.api.utils import json_view
from openprocurement.tender.cfaselectionua.procedure.state.lot import TenderLotState
from openprocurement.tender.core.procedure.models.lot import CFASelectionLot, CFASelectionPatchLot, CFASelectionPostLot
from openprocurement.tender.core.procedure.validation import (
    validate_cfa_selection_lot_operation_in_disallowed_tender_statuses,
    validate_delete_lot_related_object,
)
from openprocurement.tender.core.procedure.views.lot import TenderLotResource


@resource(
    name="closeFrameworkAgreementSelectionUA:Tender Lots",
    collection_path="/tenders/{tender_id}/lots",
    path="/tenders/{tender_id}/lots/{lot_id}",
    procurementMethodType="closeFrameworkAgreementSelectionUA",
    description="Tender lots",
)
class CFASelectionUATenderLotResource(TenderLotResource):
    state_class = TenderLotState

    @json_view(
        content_type="application/json",
        permission="create_lot",
        validators=(
            validate_item_owner("tender"),
            validate_cfa_selection_lot_operation_in_disallowed_tender_statuses,
            validate_input_data(CFASelectionPostLot),
        ),
    )
    def collection_post(self) -> Optional[dict]:
        return super().collection_post()

    @json_view(
        content_type="application/json",
        validators=(
            validate_item_owner("tender"),
            validate_cfa_selection_lot_operation_in_disallowed_tender_statuses,
            validate_input_data(CFASelectionPatchLot),
            validate_patch_data_simple(CFASelectionLot, item_name="lot"),
        ),
        permission="edit_lot",
    )
    def patch(self) -> Optional[dict]:
        return super().patch()

    @json_view(
        content_type="application/json",
        validators=(
            validate_item_owner("tender"),
            validate_cfa_selection_lot_operation_in_disallowed_tender_statuses,
            validate_delete_lot_related_object,
        ),
        permission="edit_lot",
    )
    def delete(self) -> Optional[dict]:
        return super().delete()
