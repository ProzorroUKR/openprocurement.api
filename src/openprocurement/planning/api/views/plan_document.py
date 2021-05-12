# -*- coding: utf-8 -*-
from openprocurement.planning.api.utils import opresource
from openprocurement.api.utils import json_view
from openprocurement.planning.api.validation import validate_plan_not_terminated
from openprocurement.api.validation import (
    validate_file_update,
    validate_patch_document_data,
    validate_file_upload,
)
from openprocurement.api.views.document import BaseDocumentResource
from openprocurement.planning.api.utils import save_plan, apply_patch


class CoreDocumentResource(BaseDocumentResource):
    container = "documents"
    context_name = "plan"
    db_key = "plans"

    def save(self, request, **kwargs):
        return save_plan(request)

    def apply(self, request, **kwargs):
        return apply_patch(request, **kwargs)



@opresource(
    name="Plan Documents",
    collection_path="/plans/{plan_id}/documents",
    path="/plans/{plan_id}/documents/{document_id}",
    description="Plan related binary files (PDFs, etc.)",
)
class PlansDocumentResource(CoreDocumentResource):
    @json_view(permission="view_plan")
    def collection_get(self):
        """Plan Documents List"""
        return super(PlansDocumentResource, self).collection_get()

    @json_view(permission="upload_plan_documents", validators=(validate_file_upload, validate_plan_not_terminated))
    def collection_post(self):
        """Plan Document Upload"""
        return super(PlansDocumentResource, self).collection_post()

    @json_view(permission="view_plan")
    def get(self):
        """Plan Document Read"""
        return super(PlansDocumentResource, self).get()

    @json_view(permission="upload_plan_documents", validators=(validate_file_update, validate_plan_not_terminated))
    def put(self):
        """Plan Document Update"""
        return super(PlansDocumentResource, self).put()

    @json_view(
        content_type="application/json",
        permission="upload_plan_documents",
        validators=(validate_patch_document_data, validate_plan_not_terminated),
    )
    def patch(self):
        """Plan Document Update"""
        return super(PlansDocumentResource, self).patch()
