from cornice.resource import resource

from openprocurement.api.procedure.validation import (
    update_doc_fields_on_put_document,
    validate_data_model,
    validate_input_data,
    validate_item_owner,
    validate_patch_data_simple,
    validate_upload_document,
)
from openprocurement.api.utils import json_view
from openprocurement.framework.core.procedure.models.document import (
    Document,
    PatchDocument,
    PostDocument,
)
from openprocurement.framework.core.procedure.validation import (
    validate_action_in_not_allowed_framework_status,
)
from openprocurement.framework.core.procedure.views.document import (
    CoreFrameworkChangeDocumentResource,
)
from openprocurement.framework.electroniccatalogue.constants import (
    ELECTRONIC_CATALOGUE_TYPE,
)


@resource(
    name=f"{ELECTRONIC_CATALOGUE_TYPE}:Framework Change Documents",
    collection_path="/frameworks/{framework_id}/changes/{change_id}/documents",
    path="/frameworks/{framework_id}/changes/{change_id}/documents/{document_id}",
    frameworkType=ELECTRONIC_CATALOGUE_TYPE,
    description="Framework change related binary files (PDFs, etc.)",
)
class FrameworkChangeDocumentResource(CoreFrameworkChangeDocumentResource):
    @json_view(permission="view_framework")
    def collection_get(self):
        return super().collection_get()

    @json_view(permission="view_framework")
    def get(self):
        return super().get()

    @json_view(
        validators=(
            validate_item_owner("framework"),
            validate_input_data(PostDocument, allow_bulk=True),
            validate_action_in_not_allowed_framework_status("change"),
        ),
        permission="edit_framework",
    )
    def collection_post(self):
        return super().collection_post()

    @json_view(
        validators=(
            validate_item_owner("framework"),
            validate_input_data(PostDocument),
            update_doc_fields_on_put_document,
            validate_upload_document,
            validate_data_model(Document),
            validate_action_in_not_allowed_framework_status("change"),
        ),
        permission="edit_framework",
    )
    def put(self):
        return super().put()

    @json_view(
        content_type="application/json",
        validators=(
            validate_item_owner("framework"),
            validate_input_data(PatchDocument, none_means_remove=True),
            validate_patch_data_simple(Document, item_name="document"),
            validate_action_in_not_allowed_framework_status("change"),
        ),
        permission="edit_framework",
    )
    def patch(self):
        return super().patch()
