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
from openprocurement.tender.core.procedure.validation import (
    validate_tender_change_status_with_cancellation_lot_pending,
    validate_tender_status_allows_update,
)
from openprocurement.tender.openuadefense.procedure.views.tender import (
    AboveThresholdUADefenseTenderResource,
)
from openprocurement.tender.simpledefense.procedure.models.tender import (
    PatchTender,
    PostTender,
    Tender,
)
from openprocurement.tender.simpledefense.procedure.state.tender_details import (
    SimpleDefenseTenderDetailsState,
)


@resource(
    name="simple.defense:Tenders",
    collection_path="/tenders",
    path="/tenders/{tender_id}",
    procurementMethodType="simple.defense",
    description="aboveThresholdUA.defense tenders",
    accept="application/json",
)
class SimpleDefenseTenderResource(AboveThresholdUADefenseTenderResource):
    state_class = SimpleDefenseTenderDetailsState

    @json_view(
        content_type="application/json",
        permission="create_tender",
        validators=(
            validate_input_data(PostTender),
            validate_config_data(),
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
        ),
        permission="edit_tender",
    )
    def patch(self):
        return super().patch()
