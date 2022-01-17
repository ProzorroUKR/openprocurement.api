from openprocurement.tender.core.procedure.views.bid_document import TenderBidDocumentResource
from openprocurement.api.utils import json_view
from openprocurement.tender.openeu.procedure.models.document import PostDocument, PatchDocument, Document
from openprocurement.tender.core.procedure.serializers.document import ConfidentialDocumentSerializer
from openprocurement.tender.core.procedure.validation import (
    validate_input_data,
    validate_patch_data,
    validate_item_owner,
    validate_bid_document_operation_period,
    unless_allowed_by_qualification_milestone,
    validate_upload_document,
    update_doc_fields_on_put_document,
    validate_data_model,
)
from openprocurement.tender.openua.procedure.validation import (
    validate_download_bid_document,
    validate_update_bid_document_confidentiality,
)
from openprocurement.tender.openeu.procedure.validation import (
    validate_view_bid_document,
    validate_bid_document_operation_in_bid_status,
    validate_view_bid_documents_allowed_in_bid_status,
    validate_view_financial_bid_documents_allowed_in_tender_status,
    validate_view_financial_bid_documents_allowed_in_bid_status,
)
from openprocurement.tender.cfaua.procedure.validation import (
    validate_bid_document_in_tender_status,
    validate_bid_document_operation_in_award_status,
    validate_bid_financial_document_in_tender_status,
)
from cornice.resource import resource


@resource(
    name="closeFrameworkAgreementUA:Tender Bid Documents",
    collection_path="/tenders/{tender_id}/bids/{bid_id}/documents",
    path="/tenders/{tender_id}/bids/{bid_id}/documents/{document_id}",
    procurementMethodType="closeFrameworkAgreementUA",
    description="Tender EU bidder documents",
)
class CFTenderBidDocumentResource(TenderBidDocumentResource):
    serializer_class = ConfidentialDocumentSerializer
    model_class = Document

    @json_view(
        validators=(
            validate_view_bid_document,
            validate_view_bid_documents_allowed_in_bid_status,
            validate_download_bid_document,
        ),
        permission="view_tender",
    )
    def get(self):
        return super().get()

    @json_view(
        validators=(
            validate_view_bid_document,
            validate_view_bid_documents_allowed_in_bid_status,
        ),
        permission="view_tender",
    )
    def collection_get(self):
        return super().collection_get()

    @json_view(
        validators=(
            validate_item_owner("bid"),
            validate_input_data(PostDocument, allow_bulk=True),

            validate_bid_document_operation_in_award_status,
            unless_allowed_by_qualification_milestone(
                validate_bid_document_in_tender_status,
            ),
            validate_bid_document_operation_period,
            validate_bid_document_operation_in_bid_status,
        ),
        permission="edit_bid",
    )
    def collection_post(self):
        return super().collection_post()

    @json_view(
        validators=(
            validate_item_owner("bid"),
            validate_input_data(PostDocument),

            validate_bid_document_operation_in_award_status,
            unless_allowed_by_qualification_milestone(
                validate_bid_document_in_tender_status,
            ),
            validate_bid_document_operation_period,
            validate_update_bid_document_confidentiality,

            update_doc_fields_on_put_document,
            validate_upload_document,
            validate_data_model(Document),
        ),
        permission="edit_bid",
    )
    def put(self):
        return super().put()

    @json_view(
        content_type="application/json",
        validators=(
            validate_item_owner("bid"),
            validate_input_data(PatchDocument, none_means_remove=True),
            validate_patch_data(Document, item_name="document"),
            validate_bid_document_operation_in_award_status,
            unless_allowed_by_qualification_milestone(
                validate_bid_document_in_tender_status,
            ),
            validate_bid_document_operation_period,
            validate_update_bid_document_confidentiality,
        ),
        permission="edit_bid",
    )
    def patch(self):
        return super().patch()


@resource(
    name="closeFrameworkAgreementUA:Tender Bid Eligibility Documents",
    collection_path="/tenders/{tender_id}/bids/{bid_id}/eligibility_documents",
    path="/tenders/{tender_id}/bids/{bid_id}/eligibility_documents/{document_id}",
    procurementMethodType="closeFrameworkAgreementUA",
    description="Tender EU bidder eligibility documents",
)
class TenderCFBidEligibilityDocumentResource(CFTenderBidDocumentResource):
    """ Tender EU Bid Eligibility Documents """

    container = "eligibilityDocuments"


@resource(
    name="closeFrameworkAgreementUA:Tender Bid Financial Documents",
    collection_path="/tenders/{tender_id}/bids/{bid_id}/financial_documents",
    path="/tenders/{tender_id}/bids/{bid_id}/financial_documents/{document_id}",
    procurementMethodType="closeFrameworkAgreementUA",
    description="Tender EU bidder financial documents",
)
class CFBidFinancialDocumentResource(CFTenderBidDocumentResource):
    """ Tender EU Bid Financial Documents """

    container = "financialDocuments"

    @json_view(
        validators=(
            validate_view_financial_bid_documents_allowed_in_tender_status,
            validate_view_financial_bid_documents_allowed_in_bid_status,
        ),
        permission="view_tender",
    )
    def collection_get(self):
        return super().collection_get()

    @json_view(
        validators=(
            validate_view_financial_bid_documents_allowed_in_tender_status,
            validate_view_financial_bid_documents_allowed_in_bid_status,
            validate_download_bid_document,
        ),
        permission="view_tender",
    )
    def get(self):
        return super().get()

    @json_view(
        validators=(
                validate_item_owner("bid"),
                validate_input_data(PostDocument, allow_bulk=True),

                validate_bid_document_operation_in_award_status,
                unless_allowed_by_qualification_milestone(
                    validate_bid_financial_document_in_tender_status,
                ),
                validate_bid_document_operation_period,
                validate_bid_document_operation_in_bid_status,
        ),
        permission="edit_bid",
    )
    def collection_post(self):
        return super().collection_post()

    @json_view(
        validators=(
                validate_item_owner("bid"),
                validate_input_data(PostDocument),

                validate_bid_document_operation_in_award_status,
                unless_allowed_by_qualification_milestone(
                    validate_bid_financial_document_in_tender_status,
                ),
                validate_bid_document_operation_period,
                validate_update_bid_document_confidentiality,

                update_doc_fields_on_put_document,
                validate_upload_document,
                validate_data_model(Document),
        ),
        permission="edit_bid",
    )
    def put(self):
        return super().put()

    @json_view(
        content_type="application/json",
        validators=(
                validate_item_owner("bid"),
                validate_input_data(PatchDocument, none_means_remove=True),
                validate_patch_data(Document, item_name="document"),
                validate_bid_document_operation_in_award_status,
                unless_allowed_by_qualification_milestone(
                    validate_bid_financial_document_in_tender_status,
                ),
                validate_bid_document_operation_period,
                validate_update_bid_document_confidentiality,
        ),
        permission="edit_bid",
    )
    def patch(self):
        return super().patch()


@resource(
    name="closeFrameworkAgreementUA:Tender Bid Qualification Documents",
    collection_path="/tenders/{tender_id}/bids/{bid_id}/qualification_documents",
    path="/tenders/{tender_id}/bids/{bid_id}/qualification_documents/{document_id}",
    procurementMethodType="closeFrameworkAgreementUA",
    description="Tender EU bidder qualification documents",
)
class CFBidQualificationDocumentResource(CFTenderBidDocumentResource):
    """ Tender EU Bid Qualification Documents """

    container = "qualificationDocuments"

    @json_view(
        validators=(
                validate_view_financial_bid_documents_allowed_in_tender_status,
                validate_view_financial_bid_documents_allowed_in_bid_status,
        ),
        permission="view_tender",
    )
    def collection_get(self):
        return super().collection_get()

    @json_view(
        validators=(
                validate_view_financial_bid_documents_allowed_in_tender_status,
                validate_view_financial_bid_documents_allowed_in_bid_status,
                validate_download_bid_document,
        ),
        permission="view_tender",
    )
    def get(self):
        return super().get()
