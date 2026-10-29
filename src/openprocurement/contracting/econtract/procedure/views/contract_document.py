from cornice.resource import resource

from openprocurement.api.utils import json_view
from openprocurement.contracting.core.procedure.views.contract_document import (
    ContractDocumentResource,
)
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
        permission="upload_contract_documents",
    )
    def collection_post(self):
        return super().collection_post()
