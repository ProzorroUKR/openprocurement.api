# -*- coding: utf-8 -*-
from openprocurement.api.utils import json_view
from openprocurement.api.validation import validate_file_update, validate_file_upload, validate_patch_document_data
from openprocurement.tender.core.validation import (
    validate_bid_document_operation_period,
    unless_allowed_by_qualification_milestone,
    validate_bid_document_operation_in_award_status,
)
from openprocurement.tender.core.utils import optendersresource
from openprocurement.tender.cfaua.utils import (
    bid_financial_documents_resource,
    bid_eligibility_documents_resource,
    bid_qualification_documents_resource,
)
from openprocurement.tender.openua.views.bid_document import TenderUaBidDocumentResource
from openprocurement.tender.openua.validation import (
    validate_download_bid_document,
    validate_update_bid_document_confidentiality,
)
from openprocurement.tender.openeu.validation import (
    validate_view_bid_documents_allowed_in_tender_status,
    validate_view_financial_bid_documents_allowed_in_tender_status,
    validate_view_bid_documents_allowed_in_bid_status,
    validate_view_financial_bid_documents_allowed_in_bid_status,
    validate_bid_document_operation_in_bid_status,
)
from openprocurement.tender.cfaua.validation import (
    validate_add_bid_document_not_in_allowed_tender_status,
    validate_add_bid_financial_document_not_in_allowed_tender_status,
)


@optendersresource(
    name="closeFrameworkAgreementUA:Tender Bid Documents",
    collection_path="/tenders/{tender_id}/bids/{bid_id}/documents",
    path="/tenders/{tender_id}/bids/{bid_id}/documents/{document_id}",
    procurementMethodType="closeFrameworkAgreementUA",
    description="Tender EU bidder documents",
)
class TenderEUBidDocumentResource(TenderUaBidDocumentResource):
    container = "documents"

    @json_view(
        validators=(
            validate_view_bid_documents_allowed_in_tender_status,
            validate_view_bid_documents_allowed_in_bid_status,
        ),
        permission="view_tender"
    )
    def collection_get(self):
        return super(TenderEUBidDocumentResource, self).collection_get()

    @json_view(
        validators=(
            validate_file_upload,
            validate_bid_document_operation_period,
            validate_bid_document_operation_in_award_status,
            validate_bid_document_operation_in_bid_status,
            unless_allowed_by_qualification_milestone(
                validate_add_bid_document_not_in_allowed_tender_status
            ),
        ),
        permission="edit_bid",
    )
    def collection_post(self):
        return super(TenderEUBidDocumentResource, self).collection_post()

    @json_view(
        validators=(
            validate_view_bid_documents_allowed_in_tender_status,
            validate_view_bid_documents_allowed_in_bid_status,
            validate_download_bid_document,
        ),
        permission="view_tender",
    )
    def get(self):
        return super(TenderEUBidDocumentResource, self).get()

    @json_view(
        content_type="application/json",
        validators=(
            validate_patch_document_data,
            validate_bid_document_operation_period,
            validate_bid_document_operation_in_award_status,
            validate_update_bid_document_confidentiality,
            validate_bid_document_operation_in_bid_status,
            unless_allowed_by_qualification_milestone(
                validate_add_bid_document_not_in_allowed_tender_status
            ),
        ),
        permission="edit_bid",
    )
    def patch(self):
        return super(TenderEUBidDocumentResource, self).patch()

    @json_view(
        validators=(
            validate_file_update,
            validate_bid_document_operation_period,
            validate_bid_document_operation_in_award_status,
            validate_update_bid_document_confidentiality,
            validate_bid_document_operation_in_bid_status,
            unless_allowed_by_qualification_milestone(
                validate_add_bid_document_not_in_allowed_tender_status
            ),
        ),
        permission="edit_bid",
    )
    def put(self):
        return super(TenderEUBidDocumentResource, self).put()


@bid_eligibility_documents_resource(
    name="closeFrameworkAgreementUA:Tender Bid Eligibility Documents",
    collection_path="/tenders/{tender_id}/bids/{bid_id}/eligibility_documents",
    path="/tenders/{tender_id}/bids/{bid_id}/eligibility_documents/{document_id}",
    procurementMethodType="closeFrameworkAgreementUA",
    description="Tender EU bidder eligibility documents",
)
class TenderEUBidEligibilityDocumentResource(TenderEUBidDocumentResource):
    container = "eligibilityDocuments"


@bid_financial_documents_resource(
    name="closeFrameworkAgreementUA:Tender Bid Financial Documents",
    collection_path="/tenders/{tender_id}/bids/{bid_id}/financial_documents",
    path="/tenders/{tender_id}/bids/{bid_id}/financial_documents/{document_id}",
    procurementMethodType="closeFrameworkAgreementUA",
    description="Tender EU bidder financial documents",
)
class TenderEUBidFinancialDocumentResource(TenderEUBidDocumentResource):
    container = "financialDocuments"

    @json_view(
        validators=(
            validate_view_financial_bid_documents_allowed_in_tender_status,
            validate_view_financial_bid_documents_allowed_in_bid_status,
        ),
        permission="view_tender",
    )
    def collection_get(self):
        return super(TenderEUBidFinancialDocumentResource, self).collection_get()

    @json_view(
        validators=(
            validate_view_financial_bid_documents_allowed_in_tender_status,
            validate_view_financial_bid_documents_allowed_in_bid_status,
            validate_download_bid_document,
        ),
        permission="view_tender",
    )
    def get(self):
        return super(TenderEUBidFinancialDocumentResource, self).get()

    @json_view(
        validators=(
            validate_file_upload,
            validate_bid_document_operation_period,
            validate_bid_document_operation_in_award_status,
            validate_bid_document_operation_in_bid_status,
            unless_allowed_by_qualification_milestone(
                validate_add_bid_financial_document_not_in_allowed_tender_status
            ),
        ),
        permission="edit_bid",
    )
    def collection_post(self):
        return super(TenderEUBidFinancialDocumentResource, self).collection_post()

    @json_view(
        content_type="application/json",
        validators=(
            validate_patch_document_data,
            validate_bid_document_operation_period,
            validate_bid_document_operation_in_award_status,
            validate_update_bid_document_confidentiality,
            validate_bid_document_operation_in_bid_status,
            unless_allowed_by_qualification_milestone(
                validate_add_bid_financial_document_not_in_allowed_tender_status
            ),
        ),
        permission="edit_bid",
    )
    def patch(self):
        return super(TenderEUBidFinancialDocumentResource, self).patch()

    @json_view(
        validators=(
            validate_file_update,
            validate_bid_document_operation_period,
            validate_bid_document_operation_in_award_status,
            validate_update_bid_document_confidentiality,
            validate_bid_document_operation_in_bid_status,
            unless_allowed_by_qualification_milestone(
                validate_add_bid_financial_document_not_in_allowed_tender_status
            ),
        ),
        permission="edit_bid",
    )
    def put(self):
        return super(TenderEUBidFinancialDocumentResource, self).put()


@bid_qualification_documents_resource(
    name="closeFrameworkAgreementUA:Tender Bid Qualification Documents",
    collection_path="/tenders/{tender_id}/bids/{bid_id}/qualification_documents",
    path="/tenders/{tender_id}/bids/{bid_id}/qualification_documents/{document_id}",
    procurementMethodType="closeFrameworkAgreementUA",
    description="Tender EU bidder qualification documents",
)
class TenderEUBidQualificationDocumentResource(TenderEUBidFinancialDocumentResource):
    container = "qualificationDocuments"

    @json_view(
        validators=(
            validate_file_upload,
            validate_bid_document_operation_period,
            validate_bid_document_operation_in_award_status,
            validate_bid_document_operation_in_bid_status,
            unless_allowed_by_qualification_milestone(
                validate_add_bid_document_not_in_allowed_tender_status
            ),
        ),
        permission="edit_bid",
    )
    def collection_post(self):
        return super(TenderEUBidFinancialDocumentResource, self).collection_post()

    @json_view(
        content_type="application/json",
        validators=(
            validate_patch_document_data,
            validate_bid_document_operation_period,
            validate_bid_document_operation_in_award_status,
            validate_update_bid_document_confidentiality,
            validate_bid_document_operation_in_bid_status,
            unless_allowed_by_qualification_milestone(
                validate_add_bid_document_not_in_allowed_tender_status
            ),
        ),
        permission="edit_bid",
    )
    def patch(self):
        return super(TenderEUBidFinancialDocumentResource, self).patch()

    @json_view(
        validators=(
            validate_file_update,
            validate_bid_document_operation_period,
            validate_bid_document_operation_in_award_status,
            validate_update_bid_document_confidentiality,
            validate_bid_document_operation_in_bid_status,
            unless_allowed_by_qualification_milestone(
                validate_add_bid_document_not_in_allowed_tender_status
            ),
        ),
        permission="edit_bid",
    )
    def put(self):
        return super(TenderEUBidFinancialDocumentResource, self).put()
