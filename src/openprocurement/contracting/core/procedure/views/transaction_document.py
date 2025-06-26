from cornice.resource import resource

from openprocurement.api.procedure.validation import (
    unless_admins,
    unless_bots,
    validate_input_data,
)
from openprocurement.api.utils import json_view
from openprocurement.contracting.core.procedure.models.document import (
    PostTransactionDocument,
)
from openprocurement.contracting.core.procedure.state.contract_transaction_document import (
    ContractTransactionDocumentState,
)
from openprocurement.contracting.core.procedure.validation import (
    validate_contract_owner,
)
from openprocurement.contracting.core.procedure.views.document import (
    BaseDocumentResource,
)
from openprocurement.contracting.core.procedure.views.transaction import (
    resolve_transaction,
)
from openprocurement.tender.core.procedure.views.document import resolve_document


@resource(
    name="Contract Transaction Documents",
    collection_path="/contracts/{contract_id}/transactions/{transaction_id}/documents",
    path="/contracts/{contract_id}/transactions/{transaction_id}/documents/{document_id}",
    description="Contract transaction related binary files (PDFs, etc.)",
)
class TransactionDocumentResource(BaseDocumentResource):
    item_name = "transaction"
    state_class = ContractTransactionDocumentState

    def __init__(self, request, context=None):
        super().__init__(request, context=context)
        if not context:
            resolve_transaction(request)
            resolve_document(request, self.item_name, self.container)

    @json_view(
        validators=(
            unless_bots(unless_admins(validate_contract_owner)),
            validate_input_data(PostTransactionDocument, allow_bulk=True),
        ),
        permission="edit_contract_transactions",
    )
    def post(self):
        return super().collection_post()
