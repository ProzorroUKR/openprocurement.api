from cornice.resource import resource

from openprocurement.contracting.core.procedure.views.transaction_document import TransactionDocumentResource


@resource(
    name="Contract Transaction Documents",
    path="/contracts/{contract_id}/transactions/{transaction_id}/documents",
    contractType="general",
    description="Contract transaction related binary files (PDFs, etc.)",
)
class GeneralTransactionDocumentResource(TransactionDocumentResource):
   pass
