from copy import deepcopy

from openprocurement.api.procedure.context import get_tender
from openprocurement.api.utils import raise_operation_error
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
        if isinstance(new_documents, list):
            # POST (array of docs)
            bid_docs.extend(new_documents)
        else:
            # PATCH/PUT
            bid_docs.append(doc_data)
        validate_doc_type_quantity(bid_docs, document_type="proposal", obj_name="bid")

    def validate_document_post(self, data):
        super().validate_document_post(data)
        if self.request.method == "PUT":
            # new version of an existing document
            prev_document_data = self.request.validated["document"]
            self.validate_confidentiality_change(prev_document_data, data)

    def validate_document_patch(self, before, after):
        super().validate_document_patch(before, after)
        self.validate_confidentiality_change(before, after)

    def validate_confidentiality_change(self, before, after):
        tender_status = get_tender()["status"]
        before_confidentiality = before.get("confidentiality", "public")
        after_confidentiality = after.get("confidentiality", "public")
        if tender_status != "active.tendering" and before_confidentiality != after_confidentiality:
            raise_operation_error(
                self.request,
                f"Can't update document confidentiality in current ({tender_status}) tender status",
            )

    def document_always(self, data):
        super().document_always(data)
        invalidate_pending_bid()
