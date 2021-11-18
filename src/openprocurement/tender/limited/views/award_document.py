# -*- coding: utf-8 -*-
from openprocurement.api.utils import (
    json_view,
)
from openprocurement.tender.belowthreshold.views.award_document import TenderAwardDocumentResource
from openprocurement.tender.core.utils import optendersresource
from openprocurement.api.validation import (
    validate_file_update,
    validate_patch_document_data,
    validate_file_upload,
)
from openprocurement.tender.limited.validation import (
    validate_award_document_add_not_in_pending,
    validate_document_operation_not_in_active,
)


# @optendersresource(
#     name="reporting:Tender Award Documents",
#     collection_path="/tenders/{tender_id}/awards/{award_id}/documents",
#     path="/tenders/{tender_id}/awards/{award_id}/documents/{document_id}",
#     procurementMethodType="reporting",
#     description="Tender award documents",
# )
class TenderAwardDocumentResource(TenderAwardDocumentResource):
    @json_view(
        validators=(
            validate_file_upload,
            validate_document_operation_not_in_active,
            validate_award_document_add_not_in_pending,
        ),
        permission="upload_tender_documents",
    )
    def collection_post(self):
        """Tender Award Document Upload
        """
        return super(TenderAwardDocumentResource, self).collection_post()

    @json_view(validators=(validate_file_update, validate_document_operation_not_in_active), permission="edit_tender")
    def put(self):
        """Tender Award Document Update"""
        return super(TenderAwardDocumentResource, self).put()

    @json_view(
        content_type="application/json",
        validators=(validate_patch_document_data, validate_document_operation_not_in_active),
        permission="edit_tender",
    )
    def patch(self):
        """Tender Award Document Update"""
        return super(TenderAwardDocumentResource, self).patch()


# @optendersresource(
#     name="negotiation:Tender Award Documents",
#     collection_path="/tenders/{tender_id}/awards/{award_id}/documents",
#     path="/tenders/{tender_id}/awards/{award_id}/documents/{document_id}",
#     procurementMethodType="negotiation",
#     description="Tender award documents",
# )
class TenderNegotiationAwardDocumentResource(TenderAwardDocumentResource):
    """ Tender Negotiation Award Documents Resource """


# @optendersresource(
#     name="negotiation.quick:Tender Award Documents",
#     collection_path="/tenders/{tender_id}/awards/{award_id}/documents",
#     path="/tenders/{tender_id}/awards/{award_id}/documents/{document_id}",
#     procurementMethodType="negotiation.quick",
#     description="Tender award documents",
# )
class TenderNegotiationQuickAwardDocumentResource(TenderNegotiationAwardDocumentResource):
    """ Tender Negotiation Quick Award Documents Resource """
