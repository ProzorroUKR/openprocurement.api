# -*- coding: utf-8 -*-
from openprocurement.api.utils import json_view
from openprocurement.api.validation import (
    validate_file_update,
    validate_patch_document_data,
    validate_file_upload,
)
from openprocurement.framework.core.utils import contractresource
from openprocurement.framework.core.views.document import CoreMilestoneDocumentResource
from openprocurement.framework.core.validation import (
    validate_agreement_operation_not_in_allowed_status,
    validate_contract_operation_not_in_allowed_status,
    validate_action_in_milestone_status,
    validate_restricted_access,
)
from openprocurement.framework.dps.constants import DPS_TYPE


@contractresource(
    name=f"{DPS_TYPE}:Agreements Contracts Milestone Documents",
    collection_path="/agreements/{agreement_id}/contracts/{contract_id}/milestones/{milestone_id}/documents",
    path="/agreements/{agreement_id}/contracts/{contract_id}/milestones/{milestone_id}/documents/{document_id}",
    agreementType=DPS_TYPE,
    description="Agreement contract milestone related binary files (PDFs, etc.)",
)
class MilestoneDocumentResource(CoreMilestoneDocumentResource):
    @json_view(
        validators=(
            validate_restricted_access("agreement")
        ),
        permission="view_agreement",
    )
    def collection_get(self):
        """Milestone Documents List"""
        return super(CoreMilestoneDocumentResource, self).collection_get()

    @json_view(
        permission="upload_milestone_documents",
        validators=(
            validate_file_upload,
            validate_agreement_operation_not_in_allowed_status,
            validate_contract_operation_not_in_allowed_status,
            validate_action_in_milestone_status,
        ),
    )
    def collection_post(self):
        """Milestone Document Upload"""
        return super(CoreMilestoneDocumentResource, self).collection_post()

    @json_view(
        validators=(
            validate_restricted_access("agreement")
        ),
        permission="view_agreement",
    )
    def get(self):
        """Milestone Document Read"""
        return super(CoreMilestoneDocumentResource, self).get()

    @json_view(
        permission="upload_milestone_documents",
        validators=(
            validate_file_update,
            validate_agreement_operation_not_in_allowed_status,
            validate_contract_operation_not_in_allowed_status,
            validate_action_in_milestone_status,
        ),
    )
    def put(self):
        """Milestone Document Update"""
        return super(CoreMilestoneDocumentResource, self).put()

    @json_view(
        content_type="application/json",
        permission="upload_milestone_documents",
        validators=(
            validate_patch_document_data,
            validate_agreement_operation_not_in_allowed_status,
            validate_contract_operation_not_in_allowed_status,
            validate_action_in_milestone_status,
        ),
    )
    def patch(self):
        """Milestone Document Update"""
        return super(CoreMilestoneDocumentResource, self).patch()
