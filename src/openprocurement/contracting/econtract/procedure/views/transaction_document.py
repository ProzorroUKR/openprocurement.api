from cornice.resource import resource

from openprocurement.contracting.core.procedure.views.transaction_document import (
    TransactionDocumentResource,
)


@resource(
    name="EContract Transaction Documents",
    collection_path="/contracts/{contract_id}/transactions/{transaction_id}/documents",
    path="/contracts/{contract_id}/transactions/{transaction_id}/documents/{document_id}",
    description="EContract transaction related binary files (PDFs, etc.)",
)
class EContractTransactionDocumentResource(TransactionDocumentResource):
    pass
