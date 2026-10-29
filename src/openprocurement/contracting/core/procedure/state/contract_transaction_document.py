from openprocurement.contracting.core.procedure.models.document import (
    BaseDocument,
    BasePatchDocument,
    BasePostDocument,
    PostTransactionDocument,
)
from openprocurement.contracting.core.procedure.state.document import (
    ContractDocumentState,
)


class ContractTransactionDocumentState(ContractDocumentState):
    post_data_model = BasePostDocument
    patch_data_model = BasePatchDocument
    data_model = BaseDocument
    # POST to the document path (TransactionDocumentResource.post)
    transaction_document_post_data_model = PostTransactionDocument

    document_download_confidentiality_check = False

    # --- request validation (called from the views) ---

    def validate_transaction_document_post_request(self):
        if self.request.authenticated_role not in ("bots", "admins"):
            self.validate_contract_owner()
        self.validate_input_data(self.transaction_document_post_data_model, allow_bulk=True)

    def validate_confidentiality(self, data):
        pass
