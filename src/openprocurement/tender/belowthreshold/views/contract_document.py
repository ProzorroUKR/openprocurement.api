# -*- coding: utf-8 -*-
from openprocurement.api.utils import (
    json_view,
    raise_operation_error,
)
from openprocurement.api.validation import (
    validate_file_update,
    validate_patch_document_data,
    validate_file_upload,
)

from openprocurement.tender.core.utils import optendersresource
from openprocurement.tender.core.validation import validate_role_for_contract_document_operation
from openprocurement.tender.core.views.document import CoreDocumentResource


# @optendersresource(
#     name="belowThreshold:Tender Contract Documents",
#     collection_path="/tenders/{tender_id}/contracts/{contract_id}/documents",
#     path="/tenders/{tender_id}/contracts/{contract_id}/documents/{document_id}",
#     procurementMethodType="belowThreshold",
#     description="Tender contract documents",
# )
class TenderAwardContractDocumentResource(CoreDocumentResource):
    container = "documents"
    context_name = "tender_contract"

    def validate_contract_document(self, operation):
        """ TODO move validators
        This class is inherited in openua package, but validate_contract_document function has different validators.
        For now, we have no way to use different validators on methods according to procedure type.
        """
        if self.request.validated["tender_status"] not in ["active.qualification", "active.awarded"]:
            raise_operation_error(
                self.request,
                "Can't {} document in current ({}) tender status".format(
                    operation, self.request.validated["tender_status"]
                ),
            )
        if any(
            [
                i.status != "active"
                for i in self.request.validated["tender"].lots
                if i.id
                in [
                    a.lotID
                    for a in self.request.validated["tender"].awards
                    if a.id == self.request.validated["contract"].awardID
                ]
            ]
        ):
            raise_operation_error(self.request, "Can {} document only in active lot status".format(operation))
        if self.request.validated["contract"].status not in ["pending", "pending.winner-signing", "active"]:
            raise_operation_error(self.request, "Can't {} document in current contract status".format(operation))
        return True

    @json_view(
        permission="upload_contract_documents",
        validators=(validate_file_upload, validate_role_for_contract_document_operation,)
    )
    def collection_post(self):
        """Tender Contract Document Upload
        """
        if not self.validate_contract_document("add"):
            return
        return super(TenderAwardContractDocumentResource, self).collection_post()

    @json_view(validators=(validate_file_update, validate_role_for_contract_document_operation,),
               permission="upload_contract_documents")
    def put(self):
        """Tender Contract Document Update"""
        if not self.validate_contract_document("update"):
            return
        return super(TenderAwardContractDocumentResource, self).put()

    @json_view(content_type="application/json",
               validators=(validate_patch_document_data, validate_role_for_contract_document_operation,),
               permission="upload_contract_documents")
    def patch(self):
        """Tender Contract Document Update"""
        if not self.validate_contract_document("update"):
            return
        return super(TenderAwardContractDocumentResource, self).patch()
