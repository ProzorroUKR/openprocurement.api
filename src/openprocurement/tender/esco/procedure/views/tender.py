from cornice.resource import resource

from openprocurement.api.auth import ACCR_3, ACCR_5
from openprocurement.api.procedure.validation import (
    unless_administrator,
    validate_accreditation_level,
    validate_config_data,
    validate_data_documents,
    validate_input_data,
    validate_item_owner,
    validate_patch_data_simple,
)
from openprocurement.api.utils import json_view
from openprocurement.tender.core.procedure.models.tender import TenderConfig
from openprocurement.tender.core.procedure.validation import (
    validate_item_quantity,
    validate_tender_change_status_with_cancellation_lot_pending,
    validate_tender_guarantee,
    validate_tender_status_allows_update,
)
from openprocurement.tender.core.procedure.views.tender import TendersResource
from openprocurement.tender.esco.procedure.models.tender import (
    PatchTender,
    PostTender,
    Tender,
)
from openprocurement.tender.esco.procedure.serializers.tender import (
    ESCOTenderSerializer,
)
from openprocurement.tender.esco.procedure.state.tender_details import (
    ESCOTenderDetailsState,
)


@resource(
    name="esco:Tenders",
    collection_path="/tenders",
    path="/tenders/{tender_id}",
    procurementMethodType="esco",
    description="esco tenders",
    accept="application/json",
)
class ESCOTenderResource(TendersResource):
    serializer_class = ESCOTenderSerializer
    state_class = ESCOTenderDetailsState

    @json_view(
        content_type="application/json",
        permission="create_tender",
        validators=(
            validate_input_data(PostTender),
            validate_config_data(TenderConfig),
            validate_accreditation_level(
                levels=(ACCR_3, ACCR_5),
                kind_central_levels=(ACCR_5,),
                item="tender",
                operation="creation",
                source="data",
            ),
            validate_data_documents(),
        ),
    )
    def collection_post(self):
        return super().collection_post()

    @json_view(
        content_type="application/json",
        validators=(
            unless_administrator(validate_item_owner("tender")),
            unless_administrator(
                validate_tender_status_allows_update(
                    "draft",
                    "active.tendering",
                    "active.pre-qualification",  # state class only allows status change (pre-qualification.stand-still)
                    "active.pre-qualification.stand-still",
                )
            ),
            validate_input_data(PatchTender, none_means_remove=True),
            validate_patch_data_simple(Tender, item_name="tender"),
            unless_administrator(validate_tender_change_status_with_cancellation_lot_pending),
            validate_item_quantity,
            validate_tender_guarantee,
        ),
        permission="edit_tender",
    )
    def patch(self):
        return super().patch()
