from openprocurement.tender.core.procedure.models.tender import TenderConfig
from openprocurement.tender.core.procedure.views.tender import TendersResource
from openprocurement.api.utils import json_view
from openprocurement.api.auth import ACCR_1, ACCR_2, ACCR_3, ACCR_4, ACCR_5
from openprocurement.tender.limited.procedure.state.tender_details import (
    ReportingTenderDetailsState,
    NegotiationTenderDetailsState,
)
from openprocurement.tender.limited.procedure.models.tender import (
    PostReportingTender,
    PatchReportingTender,
    ReportingTender,
    PostNegotiationTender,
    PatchNegotiationTender,
    NegotiationTender,
    PostNegotiationQuickTender,
    PatchNegotiationQuickTender,
    NegotiationQuickTender,
)
from openprocurement.tender.core.procedure.validation import (
    unless_administrator,
    validate_item_owner,
    validate_input_data,
    validate_patch_data_simple,
    validate_data_documents,
    validate_accreditation_level,
    validate_tender_status_allows_update,
    validate_config_data,
)
from cornice.resource import resource


@resource(
    name="reporting:Tenders",
    collection_path="/tenders",
    path="/tenders/{tender_id}",
    procurementMethodType="reporting",
    description="reporting tenders",
    accept="application/json",
)
class ReportingTenderResource(TendersResource):
    state_class = ReportingTenderDetailsState

    @json_view(
        content_type="application/json",
        permission="create_tender",
        validators=(
            validate_input_data(PostReportingTender),
            validate_config_data(TenderConfig, obj_name="tender"),
            validate_accreditation_level(
                levels=(ACCR_1, ACCR_3, ACCR_5),
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
                validate_tender_status_allows_update("draft", "active")
            ),
            validate_input_data(PatchReportingTender, none_means_remove=True),
            validate_patch_data_simple(ReportingTender, item_name="tender"),
            # validate_accreditation_level(
            #     levels=(ACCR_2,),
            #     item="tender",
            #     operation="update",
            # ),
        ),
        permission="edit_tender",
    )
    def patch(self):
        return super().patch()


@resource(
    name="negotiation:Tenders",
    collection_path="/tenders",
    path="/tenders/{tender_id}",
    procurementMethodType="negotiation",
    description="negotiation tenders",
    accept="application/json",
)
class NegotiationTenderResource(TendersResource):
    state_class = NegotiationTenderDetailsState

    @json_view(
        content_type="application/json",
        permission="create_tender",
        validators=(
            validate_input_data(PostNegotiationTender),
            validate_config_data(TenderConfig, obj_name="tender"),
            validate_accreditation_level(
                levels=(ACCR_3, ACCR_5),
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
                validate_tender_status_allows_update("draft", "active")
            ),
            validate_input_data(PatchNegotiationTender, none_means_remove=True),
            validate_patch_data_simple(NegotiationTender, item_name="tender"),
            # validate_accreditation_level(
            #     levels=(ACCR_4,),
            #     item="tender",
            #     operation="update",
            # ),
        ),
        permission="edit_tender",
    )
    def patch(self):
        return super().patch()


@resource(
    name="negotiation.quick:Tenders",
    collection_path="/tenders",
    path="/tenders/{tender_id}",
    procurementMethodType="negotiation.quick",
    description="negotiation tenders",
    accept="application/json",
)
class NegotiationQuickTenderResource(TendersResource):
    state_class = NegotiationTenderDetailsState

    @json_view(
        content_type="application/json",
        permission="create_tender",
        validators=(
            validate_input_data(PostNegotiationQuickTender),
            validate_config_data(TenderConfig, obj_name="tender"),
            validate_accreditation_level(
                levels=(ACCR_3, ACCR_5),
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
                validate_tender_status_allows_update("draft", "active")
            ),
            validate_input_data(PatchNegotiationQuickTender, none_means_remove=True),
            validate_patch_data_simple(NegotiationQuickTender, item_name="tender"),
            # validate_accreditation_level(
            #     levels=(ACCR_4,),
            #     item="tender",
            #     operation="update",
            # ),
        ),
        permission="edit_tender",
    )
    def patch(self):
        return super().patch()
