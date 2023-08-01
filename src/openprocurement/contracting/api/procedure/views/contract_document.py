from cornice.resource import resource

from openprocurement.tender.core.procedure.views.document import resolve_document
from openprocurement.contracting.api.procedure.views.base_document import BaseDocumentResource


@resource(
    name="Contract Documents as",
    collection_path="/contracts/{contract_id}/documents",
    path="/contracts/{contract_id}/documents/{document_id}",
    description="Contract related binary files (PDFs, etc.)",
)
class ContractDocumentResource(BaseDocumentResource):

    def __init__(self, request, context=None):
        super().__init__(request, context=context)
        if not context:
            resolve_document(request, self.item_name, self.container)
