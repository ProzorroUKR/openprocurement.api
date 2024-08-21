from copy import deepcopy

from openprocurement.api.constants import AWARD_NOTICE_DOC_REQUIRED_FROM
from openprocurement.api.context import get_request
from openprocurement.api.procedure.context import get_tender
from openprocurement.tender.core.procedure.context import get_award
from openprocurement.tender.core.procedure.state.document import BaseDocumentState
from openprocurement.tender.core.procedure.utils import tender_created_after
from openprocurement.tender.core.procedure.validation import validate_doc_type_quantity


class AwardDocumentState(BaseDocumentState):
    def validate_document_post(self, data):
        request, tender, award = get_request(), get_tender(), get_award()
        self.validate_cancellation_blocks(request, tender, lot_id=award.get("lotID"))

    def validate_document_patch(self, before, after):
        request, tender, award = get_request(), get_tender(), get_award()
        self.validate_cancellation_blocks(request, tender, lot_id=award.get("lotID"))

    def document_always(self, data):
        super().document_always(data)
        self.validate_sign_documents_already_exists(data)

    def validate_sign_documents_already_exists(self, doc_data):
        award_docs = deepcopy(get_award().get("documents", []))
        new_documents = self.request.validated["data"]
        if isinstance(new_documents, list):  # POST (array of docs)
            award_docs.extend(new_documents)
        else:  # PATCH/PUT
            award_docs.append(doc_data)
        if tender_created_after(AWARD_NOTICE_DOC_REQUIRED_FROM):
            validate_doc_type_quantity(award_docs, obj_name="award")
