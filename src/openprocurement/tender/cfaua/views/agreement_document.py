# -*- coding: utf-8 -*-
from openprocurement.api.validation import (
    validate_file_update,
    validate_patch_document_data,
    validate_file_upload,
)
from openprocurement.api.utils import (
    json_view,
    raise_operation_error,
)
from openprocurement.tender.core.views.document import CoreDocumentResource
from openprocurement.tender.cfaua.utils import agreement_resource


@agreement_resource(
    name="closeFrameworkAgreementUA:Tender Agreement Documents",
    collection_path="/tenders/{tender_id}/agreements/{agreement_id}/documents",
    path="/tenders/{tender_id}/agreements/{agreement_id}/documents/{document_id}",
    procurementMethodType="closeFrameworkAgreementUA",
    description="Tender agreement documents",
)
class TenderAwardAgreementDocumentResource(CoreDocumentResource):
    """ Tender Award Agreement Document """
    container = "documents"
    context_name = "tender_agreement"

    def validate_agreement_document(self, operation):
        """ TODO move validators
        This class is inherited from below package, but validate_agreement_document function has different validators.
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
                    if a.id in self.request.validated["agreement"].get_awards_id()
                ]
            ]
        ):
            raise_operation_error(self.request, "Can {} document only in active lot status".format(operation))
        if self.request.validated["agreement"].status not in ["pending", "active"]:
            raise_operation_error(self.request, "Can't {} document in current agreement status".format(operation))
        if any(
            [
                any([c.status == "accepted" for c in i.complaints])
                for i in self.request.validated["tender"].awards
                if i.lotID
                in [
                    a.lotID
                    for a in self.request.validated["tender"].awards
                    if a.id in self.request.validated["agreement"].get_awards_id()
                ]
            ]
        ):
            raise_operation_error(self.request, "Can't {} document with accepted complaint")
        return True

    @json_view(permission="edit_tender", validators=(validate_file_upload,))
    def collection_post(self):
        """ Tender Agreement Document Upload """
        if not self.validate_agreement_document("add"):
            return
        return super(TenderAwardAgreementDocumentResource, self).collection_post()

    @json_view(validators=(validate_file_update,), permission="edit_tender")
    def put(self):
        """ Tender Agreement Document Update """
        if not self.validate_agreement_document("update"):
            return
        return super(TenderAwardAgreementDocumentResource, self).put()

    @json_view(content_type="application/json", validators=(validate_patch_document_data,), permission="edit_tender")
    def patch(self):
        """ Tender Agreement Document Update """
        if not self.validate_agreement_document("update"):
            return
        return super(TenderAwardAgreementDocumentResource, self).patch()
