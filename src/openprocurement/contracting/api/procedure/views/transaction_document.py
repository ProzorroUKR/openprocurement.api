from cornice.resource import resource

from openprocurement.contracting.core.procedure.views.transaction_document import (
    TransactionDocumentResource,
)


@resource(
    name="Contract Transaction Documents",
    collection_path="/contracts/{contract_id}/transactions/{transaction_id}/documents",
    path="/contracts/{contract_id}/transactions/{transaction_id}/documents/{document_id}",
    contractType="general",
    description="Contract transaction related binary files (PDFs, etc.)",
)
class GeneralTransactionDocumentResource(TransactionDocumentResource):
    pass
