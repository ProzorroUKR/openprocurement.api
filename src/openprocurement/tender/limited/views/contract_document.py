# -*- coding: utf-8 -*-
from openprocurement.api.utils import json_view
from openprocurement.tender.core.utils import optendersresource

from openprocurement.api.validation import (
    validate_file_update,
    validate_patch_document_data,
    validate_file_upload,
)
from openprocurement.tender.belowthreshold.views.contract_document import (
    TenderAwardContractDocumentResource as BaseTenderAwardContractDocumentResource,
)
from openprocurement.tender.limited.validation import (
    validate_document_operation_not_in_active,
    validate_contract_document_operation_not_in_allowed_contract_status,
)


# @optendersresource(
#     name="reporting:Tender Contract Documents",
#     collection_path="/tenders/{tender_id}/contracts/{contract_id}/documents",
#     path="/tenders/{tender_id}/contracts/{contract_id}/documents/{document_id}",
#     procurementMethodType="reporting",
#     description="Tender contract documents",
# )
class TenderAwardContractDocumentResource(BaseTenderAwardContractDocumentResource):

    def validate_contract_document(self, operation):
        return True

    @json_view(
        permission="edit_tender",
        validators=(
            validate_file_upload,
            validate_document_operation_not_in_active,
            validate_contract_document_operation_not_in_allowed_contract_status,
        ),
    )
    def collection_post(self):
        """Tender Contract Document Upload
        """
        return super(TenderAwardContractDocumentResource, self).collection_post()

    @json_view(
        validators=(
            validate_file_update,
            validate_document_operation_not_in_active,
            validate_contract_document_operation_not_in_allowed_contract_status,
        ),
        permission="edit_tender",
    )
    def put(self):
        """Tender Contract Document Update"""
        return super(TenderAwardContractDocumentResource, self).put()

    @json_view(
        content_type="application/json",
        validators=(
            validate_patch_document_data,
            validate_document_operation_not_in_active,
            validate_contract_document_operation_not_in_allowed_contract_status,
        ),
        permission="edit_tender",
    )
    def patch(self):
        """Tender Contract Document Update"""
        return super(TenderAwardContractDocumentResource, self).patch()


# @optendersresource(
#     name="negotiation:Tender Contract Documents",
#     collection_path="/tenders/{tender_id}/contracts/{contract_id}/documents",
#     path="/tenders/{tender_id}/contracts/{contract_id}/documents/{document_id}",
#     procurementMethodType="negotiation",
#     description="Tender contract documents",
# )
class TenderNegotiationAwardContractDocumentResource(TenderAwardContractDocumentResource):
    """ Tender Negotiation Award Contract Document Resource """


# @optendersresource(
#     name="negotiation.quick:Tender Contract Documents",
#     collection_path="/tenders/{tender_id}/contracts/{contract_id}/documents",
#     path="/tenders/{tender_id}/contracts/{contract_id}/documents/{document_id}",
#     procurementMethodType="negotiation.quick",
#     description="Tender contract documents",
# )
class TenderNegotiationQuickAwardContractDocumentResource(TenderNegotiationAwardContractDocumentResource):
    """ Tender Negotiation Quick Award Contract Document Resource """
