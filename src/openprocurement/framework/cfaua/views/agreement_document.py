from openprocurement.api.utils import json_view
from openprocurement.api.validation import (
    validate_file_update,
    validate_patch_document_data,
    validate_file_upload,
)
from openprocurement.framework.cfaua.validation import validate_document_operation_on_agreement_status
from openprocurement.framework.core.utils import agreementsresource
from openprocurement.framework.core.views.document import CoreAgreementDocumentResource


@agreementsresource(
    name="cfaua:Agreement Documents",
    collection_path="/agreements/{agreement_id}/documents",
    path="/agreements/{agreement_id}/documents/{document_id}",
    agreementType="cfaua",
    description="Agreement Documents",
)
class AgreementDocumentsResource(CoreAgreementDocumentResource):

    @json_view(permission="view_agreement")
    def collection_get(self):
        """Plan Documents List"""
        return super(AgreementDocumentsResource, self).collection_get()

    @json_view(
        permission="upload_agreement_documents",
        validators=(
            validate_file_upload,
            validate_document_operation_on_agreement_status,
        ),
    )
    def collection_post(self):
        """ Agreement Document Upload"""
        return super(AgreementDocumentsResource, self).collection_post()

    @json_view(permission="view_agreement")
    def get(self):
        """Plan Document Read"""
        return super(AgreementDocumentsResource, self).get()

    @json_view(
        permission="upload_agreement_documents",
        validators=(
            validate_file_update,
            validate_document_operation_on_agreement_status,
        ),
    )
    def put(self):
        """ Agreement Document Update"""
        return super(AgreementDocumentsResource, self).put()

    @json_view(
        content_type="application/json",
        permission="upload_agreement_documents",
        validators=(
            validate_patch_document_data,
            validate_document_operation_on_agreement_status,
        ),
    )
    def patch(self):
        """ Agreement Document Update """
        return super(AgreementDocumentsResource, self).patch()
