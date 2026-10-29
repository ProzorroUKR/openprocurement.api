from cornice.resource import resource

from openprocurement.api.utils import json_view
from openprocurement.contracting.core.procedure.views.contract_document import (
    ContractDocumentResource as BaseContractDocumentResource,
)


@resource(
    name="Contract Documents",
    collection_path="/contracts/{contract_id}/documents",
    path="/contracts/{contract_id}/documents/{document_id}",
    contractType="contract",
    description="Contract related binary files (PDFs, etc.)",
)
class ContractDocumentResource(BaseContractDocumentResource):
    @json_view(
        permission="upload_contract_documents",
    )
    def collection_post(self):
        return super().collection_post()

    @json_view(
        permission="edit_contract_documents",
    )
    def put(self):
        return super().put()

    @json_view(
        content_type="application/json",
        permission="edit_contract_documents",
    )
    def patch(self):
        return super().patch()
