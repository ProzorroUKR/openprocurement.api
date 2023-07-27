from openprocurement.api.utils import json_view

from openprocurement.contracting.core.procedure.views.transaction import resolve_transaction
from openprocurement.tender.core.procedure.views.document import resolve_document
from openprocurement.contracting.core.procedure.views.document import BaseDocumentResource
from openprocurement.tender.core.procedure.validation import (
    validate_input_data,
    unless_bots,
    unless_admins,
    validate_item_owner,
)
from openprocurement.contracting.core.procedure.models.document import PostTransactionDocument


class TransactionDocumentResource(BaseDocumentResource):
    item_name = "transaction"

    def __init__(self, request, context=None):
        super().__init__(request, context=context)
        if not context:
            resolve_transaction(request)
            resolve_document(request, self.item_name, self.container)

    @json_view(
        validators=(
            unless_bots(unless_admins(validate_item_owner("contract"))),
            validate_input_data(PostTransactionDocument, allow_bulk=True),
        ),
        permission="edit_contract_transactions",
    )
    def post(self):
        return super().collection_post()
