# -*- coding: utf-8 -*-
from openprocurement.api.utils import (
    json_view,
)
from openprocurement.tender.belowthreshold.views.tender_document import (
    TenderDocumentResource,
)
from openprocurement.tender.core.utils import optendersresource
from openprocurement.api.validation import (
    validate_file_update,
    validate_file_upload,
    validate_patch_document_data,
)
from openprocurement.tender.limited.validation import validate_operation_with_document_not_in_active_status


# @optendersresource(
#     name="reporting:Tender Documents",
#     collection_path="/tenders/{tender_id}/documents",
#     path="/tenders/{tender_id}/documents/{document_id}",
#     procurementMethodType="reporting",
#     description="Tender related binary files (PDFs, etc.)",
# )
class TenderDocumentResource(TenderDocumentResource):
    @json_view(
        permission="upload_tender_documents",
        validators=(validate_file_upload, validate_operation_with_document_not_in_active_status),
    )
    def collection_post(self):
        """Tender Document Upload"""
        return super(TenderDocumentResource, self).collection_post()

    @json_view(
        permission="upload_tender_documents",
        validators=(validate_file_update, validate_operation_with_document_not_in_active_status),
    )
    def put(self):
        """Tender Document Update"""
        return super(TenderDocumentResource, self).put()

    @json_view(
        content_type="application/json",
        permission="upload_tender_documents",
        validators=(validate_patch_document_data, validate_operation_with_document_not_in_active_status),
    )
    def patch(self):
        """Tender Document Update"""
        return super(TenderDocumentResource, self).patch()


# @optendersresource(
#     name="negotiation:Tender Documents",
#     collection_path="/tenders/{tender_id}/documents",
#     path="/tenders/{tender_id}/documents/{document_id}",
#     procurementMethodType="negotiation",
#     description="Tender related binary files (PDFs, etc.)",
# )
class TenderNegotiationDocumentResource(TenderDocumentResource):
    """ Tender Negotiation Document Resource """


# @optendersresource(
#     name="negotiation.quick:Tender Documents",
#     collection_path="/tenders/{tender_id}/documents",
#     path="/tenders/{tender_id}/documents/{document_id}",
#     procurementMethodType="negotiation.quick",
#     description="Tender related binary files (PDFs, etc.)",
# )
class TenderNegotiationQuickDocumentResource(TenderNegotiationDocumentResource):
    """ Tender Negotiation Quick Document Resource """
