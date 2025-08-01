from cornice.resource import resource

from openprocurement.api.procedure.validation import unless_admins, validate_input_data
from openprocurement.api.utils import json_view
from openprocurement.contracting.core.procedure.validation import (
    validate_contract_document_operation_not_in_allowed_contract_status,
    validate_contract_participant,
    validate_contract_signature_operation,
)
from openprocurement.contracting.core.procedure.views.contract_document import (
    ContractDocumentResource,
)
from openprocurement.contracting.econtract.procedure.models.document import PostDocument
from openprocurement.contracting.econtract.procedure.state.contract_document import (
    EContractDocumentState,
)


@resource(
    name="EContract Documents",
    collection_path="/contracts/{contract_id}/documents",
    path="/contracts/{contract_id}/documents/{document_id}",
    contractType="eContract",
    description="EContract related binary files (PDFs, etc.)",
    request_method=("POST", "GET"),
)
class EContractDocumentResource(ContractDocumentResource):
    state_class = EContractDocumentState

    @json_view(
        validators=(
            unless_admins(validate_contract_participant),
            validate_input_data(PostDocument, allow_bulk=True),
            validate_contract_document_operation_not_in_allowed_contract_status,
            validate_contract_signature_operation,
        ),
        permission="upload_contract_documents",
    )
    def collection_post(self):
        return super().collection_post()
