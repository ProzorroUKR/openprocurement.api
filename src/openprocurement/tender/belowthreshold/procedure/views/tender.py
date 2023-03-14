from openprocurement.api.utils import json_view
from openprocurement.api.auth import ACCR_1, ACCR_5, ACCR_2
from openprocurement.tender.core.procedure.models.tender import TenderConfig
from openprocurement.tender.core.procedure.views.tender import TendersResource
from openprocurement.tender.belowthreshold.procedure.models.tender import PostTender, PatchTender, Tender
from openprocurement.tender.belowthreshold.procedure.state.tender_details import TenderDetailsState
from openprocurement.tender.belowthreshold.constants import BELOW_THRESHOLD
from openprocurement.tender.core.procedure.validation import (
    unless_administrator,
    validate_item_owner,
    validate_input_data,
    validate_patch_data_simple,
    validate_data_documents,
    validate_accreditation_level,
    validate_tender_status_allows_update,
    validate_item_quantity,
    validate_tender_guarantee,
    validate_data_model,
    validate_config_data,
)
from cornice.resource import resource


@resource(
    name="belowThreshold:Tenders",
    collection_path="/tenders",
    path="/tenders/{tender_id}",
    procurementMethodType="belowThreshold",
    description="BelowThreshold tenders",
    accept="application/json",
)
class BelowThresholdTenderResource(TendersResource):
    state_class = TenderDetailsState

    @json_view(
        content_type="application/json",
        permission="create_tender",
        validators=(
            validate_input_data(PostTender),
            validate_config_data(TenderConfig, obj_name="tender"),
            validate_accreditation_level(
                levels=(ACCR_1, ACCR_5),
                kind_central_levels=(ACCR_5,),
                item="tender",
                operation="creation",
                source="data"
            ),
            validate_data_documents(),
        ),
    )
    def collection_post(self):
        return super().collection_post()

    @json_view(
        content_type="application/json",
        validators=(
            unless_administrator(
                validate_item_owner("tender")
            ),
            unless_administrator(
                validate_tender_status_allows_update("draft", "active.enquiries")
            ),
            validate_input_data(PatchTender, none_means_remove=True),
            validate_patch_data_simple(Tender, item_name="tender"),
            # validate_accreditation_level(
            #     levels=(ACCR_2,),
            #     item="tender",
            #     operation="update",
            # ),
            validate_item_quantity,
            validate_tender_guarantee,
        ),
        permission="edit_tender",
    )
    def patch(self):
        return super().patch()
