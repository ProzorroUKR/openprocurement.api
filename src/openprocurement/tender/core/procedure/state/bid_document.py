from openprocurement.api.context import get_request
from openprocurement.api.utils import raise_operation_error
from openprocurement.tender.core.procedure.context import get_bid
from openprocurement.tender.core.procedure.state.document import BaseDocumentState
from openprocurement.tender.core.procedure.utils import is_sign_doc
from openprocurement.tender.core.procedure.validation import validate_sign_doc_quantity


class BidDocumentState(BaseDocumentState):
    def validate_document_post(self, data):
        self.validate_proposal_document_already_exists(data)

    def validate_document_patch(self, before, after):
        self.validate_proposal_document_already_exists(after)

    def validate_proposal_document_already_exists(self, doc_data):
        if is_sign_doc(doc_data, doc_type="proposal"):
            bid = get_bid()
            for doc in bid.get("documents", []):
                if is_sign_doc(doc, doc_type="proposal") and doc["id"] != doc_data.get("id"):
                    raise_operation_error(
                        get_request(),
                        "Proposal document already exists in tender",
                        name="documents",
                        status=422,
                    )
        documents = self.request.validated["data"]
        if isinstance(documents, list) and len(documents) > 1:
            validate_sign_doc_quantity(documents, doc_type="proposal")
