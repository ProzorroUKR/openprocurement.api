from copy import deepcopy

from openprocurement.tender.core.procedure.context import get_bid
from openprocurement.tender.core.procedure.state.document import BaseDocumentState
from openprocurement.tender.core.procedure.state.utils import invalidate_pending_bid
from openprocurement.tender.core.procedure.validation import validate_doc_type_quantity


class BidDocumentState(BaseDocumentState):
    check_edrpou_confidentiality = False
    allow_deletion = True

    def validate_sign_documents_already_exists(self, doc_data, doc_envelope):
        bid_docs = deepcopy(get_bid().get(doc_envelope, []))
        new_documents = self.request.validated["data"]
        if isinstance(new_documents, list):  # POST (array of docs)
            bid_docs.extend(new_documents)
        else:  # PATCH/PUT
            bid_docs.append(doc_data)
        validate_doc_type_quantity(bid_docs, document_type="proposal", obj_name="bid")

    def document_always(self, data):
        super().document_always(data)
        invalidate_pending_bid()
