from cornice.resource import resource

from openprocurement.api.procedure.validation import unless_admins, validate_input_data
from openprocurement.api.utils import json_view
from openprocurement.contracting.core.procedure.validation import (
    validate_contract_change_action_not_in_allowed_contract_status,
    validate_contract_change_update_not_in_allowed_change_status,
    validate_contract_participant,
)
from openprocurement.contracting.core.procedure.views.change import resolve_change
from openprocurement.contracting.core.procedure.views.document import (
    BaseDocumentResource,
)
from openprocurement.contracting.econtract.procedure.models.document import (
    PostChangeDocument,
)
from openprocurement.contracting.econtract.procedure.state.change_documents import (
    EContractChangeDocumentState,
)
from openprocurement.tender.core.procedure.views.document import resolve_document


@resource(
    name="EContract change documents",
    collection_path="/contracts/{contract_id}/changes/{change_id}/documents",
    path="/contracts/{contract_id}/changes/{change_id}/documents/{document_id}",
    contractType="eContract",
    description="EContract changes related binary files (PDFs, etc.)",
    request_method=("POST", "GET"),
)
class EContractChangesDocumentResource(BaseDocumentResource):
    state_class = EContractChangeDocumentState
    item_name = "change"

    def __init__(self, request, context=None):
        super().__init__(request, context=context)
        if not context:
            resolve_change(request)
            resolve_document(request, self.item_name, self.container)

    @json_view(
        validators=(
            unless_admins(validate_contract_participant),
            validate_input_data(PostChangeDocument, allow_bulk=True),
            validate_contract_change_action_not_in_allowed_contract_status,
            validate_contract_change_update_not_in_allowed_change_status,
        ),
        permission="edit_contract",
    )
    def collection_post(self):
        return super().collection_post()
