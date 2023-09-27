from cornice.resource import resource

from openprocurement.contracting.core.procedure.views.transaction_document import TransactionDocumentResource


@resource(
    name="EContract Transaction Documents",
    path="/contracts/{contract_id}/transactions/{transaction_id}/documents",
    contractType="econtract",
    description="EContract transaction related binary files (PDFs, etc.)",
)
class GeneralTransactionDocumentResource(TransactionDocumentResource):
   pass
