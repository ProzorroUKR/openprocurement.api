from cornice.resource import resource

from openprocurement.api.utils import json_view
from openprocurement.framework.core.procedure.models.document import PostDocument, PatchDocument, Document
from openprocurement.framework.core.procedure.validation import (
    validate_agreement_operation_not_in_allowed_status,
    validate_contract_operation_not_in_allowed_status,
    validate_action_in_milestone_status,
)
from openprocurement.framework.core.procedure.views.document import CoreMilestoneDocumentResource
from openprocurement.framework.dps.constants import DPS_TYPE
from openprocurement.api.procedure.validation import (
    validate_patch_data_simple,
    validate_data_model,
    validate_input_data, validate_item_owner, validate_upload_document, update_doc_fields_on_put_document,
)


@resource(
    name=f"{DPS_TYPE}:Agreements Contracts Milestone Documents",
    collection_path="/agreements/{agreement_id}/contracts/{contract_id}/milestones/{milestone_id}/documents",
    path="/agreements/{agreement_id}/contracts/{contract_id}/milestones/{milestone_id}/documents/{document_id}",
    description="Agreement contract milestone related binary files (PDFs, etc.)",
    agreementType=DPS_TYPE,
)
class MilestoneDocumentResource(CoreMilestoneDocumentResource):
    @json_view(
        permission="view_framework",
    )
    def collection_get(self):
        return super().collection_get()

    @json_view(
        permission="view_framework",
    )
    def get(self):
        return super().get()

    @json_view(
        validators=(
                validate_item_owner("agreement"),
                validate_input_data(PostDocument, allow_bulk=True),
                validate_agreement_operation_not_in_allowed_status,
                validate_contract_operation_not_in_allowed_status,
                validate_action_in_milestone_status,
        ),
        permission="edit_agreement",
    )
    def collection_post(self):
        return super().collection_post()

    @json_view(
        validators=(
                validate_item_owner("agreement"),
                validate_input_data(PostDocument),
                update_doc_fields_on_put_document,
                validate_upload_document,
                validate_data_model(Document),
                validate_agreement_operation_not_in_allowed_status,
                validate_contract_operation_not_in_allowed_status,
                validate_action_in_milestone_status,
        ),
        permission="edit_agreement",
    )
    def put(self):
        return super().put()

    @json_view(
        content_type="application/json",
        validators=(
                validate_item_owner("agreement"),
                validate_input_data(PatchDocument, none_means_remove=True),
                validate_patch_data_simple(Document, item_name="document"),
                validate_agreement_operation_not_in_allowed_status,
                validate_contract_operation_not_in_allowed_status,
                validate_action_in_milestone_status,
        ),
        permission="edit_agreement",
    )
    def patch(self):
        return super().patch()
