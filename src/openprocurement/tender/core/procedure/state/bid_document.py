from copy import deepcopy

from openprocurement.api.constants import BID_PROPOSAL_DOC_REQUIRED_FROM
from openprocurement.tender.core.procedure.context import get_bid
from openprocurement.tender.core.procedure.state.document import BaseDocumentState
from openprocurement.tender.core.procedure.utils import tender_created_after
from openprocurement.tender.core.procedure.validation import validate_doc_type_quantity


class BidDocumentState(BaseDocumentState):
    def validate_document_post(self, data):
        self.validate_sign_documents_already_exists(data)

    def validate_document_patch(self, before, after):
        self.validate_sign_documents_already_exists(after)

    def validate_sign_documents_already_exists(self, doc_data):
        bid_docs = deepcopy(get_bid().get("documents", []))
        new_documents = self.request.validated["data"]
        if isinstance(new_documents, list):  # POST (array of docs)
            bid_docs.extend(new_documents)
        else:  # PATCH/PUT
            bid_docs.append(doc_data)
        if tender_created_after(BID_PROPOSAL_DOC_REQUIRED_FROM):
            validate_doc_type_quantity(bid_docs, document_type="proposal", obj_name="bid")

    def document_always(self, data):
        super().document_always(data)
        self.invalidate_pending_bid()

    def invalidate_pending_bid(self):
        bid = get_bid()
        if tender_created_after(BID_PROPOSAL_DOC_REQUIRED_FROM) and bid.get("status") == "pending":
            bid["status"] = "invalid"
