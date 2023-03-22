# -*- coding: utf-8 -*-
from openprocurement.api.utils import json_view
from openprocurement.api.validation import (
    validate_file_update,
    validate_patch_document_data,
    validate_file_upload,
)
from openprocurement.framework.core.utils import frameworksresource
from openprocurement.framework.core.views.document import CoreFrameworkDocumentResource
from openprocurement.framework.core.validation import (
    validate_framework_document_operation_not_in_allowed_status,
)
from openprocurement.framework.dps.constants import DPS_TYPE


@frameworksresource(
    name=f"{DPS_TYPE}:Framework Documents",
    collection_path="/frameworks/{framework_id}/documents",
    path="/frameworks/{framework_id}/documents/{document_id}",
    frameworkType=DPS_TYPE,
    description="Framework related binary files (PDFs, etc.)",
)
class FrameworkDocumentResource(CoreFrameworkDocumentResource):
    @json_view(permission="view_framework")
    def collection_get(self):
        """Contract Documents List"""
        return super(FrameworkDocumentResource, self).collection_get()

    @json_view(
        permission="upload_framework_documents",
        validators=(
            validate_file_upload,
            validate_framework_document_operation_not_in_allowed_status,
        ),
    )
    def collection_post(self):
        """Framework Document Upload"""
        return super(FrameworkDocumentResource, self).collection_post()

    @json_view(permission="view_framework")
    def get(self):
        """Framework Document Read"""
        return super(FrameworkDocumentResource, self).get()

    @json_view(
        permission="upload_framework_documents",
        validators=(
            validate_file_update,
            validate_framework_document_operation_not_in_allowed_status,
        ),
    )
    def put(self):
        """Framework Document Update"""
        return super(FrameworkDocumentResource, self).put()

    @json_view(
        content_type="application/json",
        permission="upload_framework_documents",
        validators=(
            validate_patch_document_data,
            validate_framework_document_operation_not_in_allowed_status,
        ),
    )
    def patch(self):
        """Framework Document Update"""
        return super(FrameworkDocumentResource, self).patch()
