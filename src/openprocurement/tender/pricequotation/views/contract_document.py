# -*- coding: utf-8 -*-
from openprocurement.api.utils import (
    json_view,
)
from openprocurement.api.validation import (
    validate_file_update,
    validate_patch_document_data,
    validate_file_upload,
)
from openprocurement.tender.core.utils import optendersresource
from openprocurement.tender.core.validation import validate_role_for_contract_document_operation
from openprocurement.tender.belowthreshold.views.contract_document import TenderAwardContractDocumentResource
from openprocurement.tender.pricequotation.constants import PQ
from openprocurement.tender.pricequotation.validation import validate_contract_document_operation


# @optendersresource(
#     name="{}:Tender Contract Documents".format(PMT),
#     collection_path="/tenders/{tender_id}/contracts/{contract_id}/documents",
#     path="/tenders/{tender_id}/contracts/{contract_id}/documents/{document_id}",
#     procurementMethodType=PMT,
#     description="Tender contract documents",
# )
class PQTenderAwardContractDocumentResource(TenderAwardContractDocumentResource):

    def validate_contract_document(self, operation):
        return True

    @json_view(
        permission="upload_contract_documents",
        validators=(
            validate_file_upload,
            validate_role_for_contract_document_operation,
            validate_contract_document_operation,
        )
    )
    def collection_post(self):
        """Tender Contract Document Upload
        """
        return super(PQTenderAwardContractDocumentResource, self).collection_post()

    @json_view(
        validators=(
            validate_file_update,
            validate_role_for_contract_document_operation,
            validate_contract_document_operation,
        ),
        permission="upload_contract_documents"
    )
    def put(self):
        """Tender Contract Document Update"""
        return super(PQTenderAwardContractDocumentResource, self).put()

    @json_view(
        content_type="application/json",
        validators=(
            validate_patch_document_data,
            validate_role_for_contract_document_operation,
            validate_contract_document_operation,
        ),
        permission="upload_contract_documents"
    )
    def patch(self):
        """Tender Contract Document Update"""
        return super(PQTenderAwardContractDocumentResource, self).patch()
