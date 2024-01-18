from openprocurement.api.utils import json_view
from openprocurement.api.auth import ACCR_1, ACCR_5, ACCR_2
from openprocurement.tender.core.procedure.models.tender import TenderConfig
from openprocurement.tender.core.procedure.serializers.config import TenderConfigSerializer
from openprocurement.tender.core.procedure.views.tender import TendersResource
from openprocurement.tender.cfaselectionua.procedure.models.tender import PostTender, PatchTender, Tender
from openprocurement.tender.cfaselectionua.procedure.state.tender_details import CFASelectionTenderDetailsState
from openprocurement.tender.cfaselectionua.procedure.validation import unless_selection_bot
from openprocurement.tender.core.procedure.validation import (
    validate_tender_status_allows_update,
    validate_item_quantity,
    validate_tender_guarantee,
    validate_tender_change_status_with_cancellation_lot_pending,
)
from openprocurement.api.procedure.validation import (
    validate_patch_data_simple,
    validate_config_data,
    validate_input_data,
    validate_data_documents,
    validate_item_owner,
    unless_administrator,
    validate_accreditation_level,
)
from cornice.resource import resource
from pyramid.security import Allow


@resource(
    name="closeFrameworkAgreementSelectionUA:Tenders",
    collection_path="/tenders",
    path="/tenders/{tender_id}",
    procurementMethodType="closeFrameworkAgreementSelectionUA",
    description="closeFrameworkAgreementSelectionUA tenders",
    accept="application/json",
)
class CFASelectionTenderResource(TendersResource):
    state_class = CFASelectionTenderDetailsState

    def __acl__(self):
        acl = super().__acl__()
        acl.append(
            (Allow, "g:agreement_selection", "edit_tender"),
        )
        return acl

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
            unless_selection_bot(  # TODO: make a distinct endpoint for unless_selection_bot
                unless_administrator(
                    validate_item_owner("tender")
                )
            ),
            unless_administrator(
                validate_tender_status_allows_update(
                    "draft",
                    "draft.pending",   # only selection_bot can update here ?
                    "active.enquiries",
                    "active.tendering",
                    "active.pre-qualification",  # state class only allows status change  pre-qualification.stand-still
                    "active.qualification",  # state class only allows status change to qualification.stand-still
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
