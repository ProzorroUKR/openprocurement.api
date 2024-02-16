from cornice.resource import resource

from openprocurement.contracting.core.procedure.views.contract_document import (
    ContractDocumentResource,
)


@resource(
    name="General Contract Documents",
    collection_path="/contracts/{contract_id}/documents",
    path="/contracts/{contract_id}/documents/{document_id}",
    contractType="general",
    description="General contract related binary files (PDFs, etc.)",
)
class GeneralContractDocumentResource(ContractDocumentResource):
    pass
