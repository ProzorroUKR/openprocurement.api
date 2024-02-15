from cornice.resource import resource

from openprocurement.api.auth import ACCR_1, ACCR_5
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
from openprocurement.tender.belowthreshold.constants import BELOW_THRESHOLD
from openprocurement.tender.belowthreshold.procedure.models.tender import (
    PostTender,
    Tender,
)
from openprocurement.tender.belowthreshold.procedure.state.tender_details import (
    BelowThresholdTenderDetailsState,
)
from openprocurement.tender.core.procedure.models.tender import TenderConfig
from openprocurement.tender.core.procedure.validation import (
    validate_input_data_from_resolved_model,
    validate_item_quantity,
    validate_tender_guarantee,
    validate_tender_status_allows_update,
)
from openprocurement.tender.core.procedure.views.tender import TendersResource


@resource(
    name=f"{BELOW_THRESHOLD}:Tenders",
    collection_path="/tenders",
    path="/tenders/{tender_id}",
    procurementMethodType=BELOW_THRESHOLD,
    description="BelowThreshold tenders",
    accept="application/json",
)
class BelowThresholdTenderResource(TendersResource):
    state_class = BelowThresholdTenderDetailsState

    @json_view(
        content_type="application/json",
        permission="create_tender",
        validators=(
            validate_input_data(PostTender),
            validate_config_data(TenderConfig),
            validate_accreditation_level(
                levels=(ACCR_1, ACCR_5),
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
                    "active.enquiries",
                    "active.pre-qualification",  # state class only allows status change (pre-qualification.stand-still)
                    "active.tendering",
                )
            ),
            validate_input_data_from_resolved_model(none_means_remove=True),
            validate_patch_data_simple(Tender, item_name="tender"),
            validate_item_quantity,
            validate_tender_guarantee,
        ),
        permission="edit_tender",
    )
    def patch(self):
        return super().patch()
