from cornice.resource import resource

from openprocurement.contracting.core.procedure.views.contract_document import ContractDocumentResource


@resource(
    name="EContract Documents",
    collection_path="/contracts/{contract_id}/documents",
    path="/contracts/{contract_id}/documents/{document_id}",
    contractType="econtract",
    description="EContract related binary files (PDFs, etc.)",
)
class EContractDocumentResource(ContractDocumentResource):
    pass
