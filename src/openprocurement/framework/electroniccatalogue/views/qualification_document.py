# -*- coding: utf-8 -*-
from openprocurement.api.utils import json_view
from openprocurement.api.validation import (
    validate_file_update,
    validate_patch_document_data,
    validate_file_upload,
)
from openprocurement.framework.core.utils import qualificationsresource
from openprocurement.framework.core.views.document import CoreQualificationDocumentResource
from openprocurement.framework.core.validation import (
    validate_document_operation_in_not_allowed_status,
)
from openprocurement.framework.electroniccatalogue.constants import ELECTRONIC_CATALOGUE_TYPE


@qualificationsresource(
    name=f"{ELECTRONIC_CATALOGUE_TYPE}:Qualification Documents",
    collection_path="/qualifications/{qualification_id}/documents",
    path="/qualifications/{qualification_id}/documents/{document_id}",
    qualificationType=ELECTRONIC_CATALOGUE_TYPE,
    description="Qualification related binary files (PDFs, etc.)",
)
class QualificationDocumentResource(CoreQualificationDocumentResource):
    context_name = "qualification"

    @json_view(permission="view_qualification")
    def collection_get(self):
        """Qualification Documents List"""
        return super(QualificationDocumentResource, self).collection_get()

    @json_view(
        permission="edit_qualification",
        validators=(
            validate_document_operation_in_not_allowed_status,
            validate_file_upload,
        ),
    )
    def collection_post(self):
        """Qualification Document Upload"""
        return super(QualificationDocumentResource, self).collection_post()

    @json_view(permission="view_qualification")
    def get(self):
        """qualification Document Read"""
        return super(QualificationDocumentResource, self).get()

    @json_view(
        permission="edit_qualification",
        validators=(
            validate_document_operation_in_not_allowed_status,
            validate_file_update,
        ),
    )
    def put(self):
        """Qualification Document Update"""
        return super(QualificationDocumentResource, self).put()

    @json_view(
        content_type="application/json",
        permission="edit_qualification",
        validators=(
            validate_document_operation_in_not_allowed_status,
            validate_patch_document_data,
        ),
    )
    def patch(self):
        """Qualification Document Update"""
        return super(QualificationDocumentResource, self).patch()
