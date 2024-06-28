from copy import deepcopy

from openprocurement.api.constants import NOTICE_DOC_REQUIRED_FROM
from openprocurement.api.procedure.context import get_tender
from openprocurement.tender.core.procedure.state.document import BaseDocumentState
from openprocurement.tender.core.procedure.utils import tender_created_after
from openprocurement.tender.core.procedure.validation import validate_doc_type_quantity


class TenderDocumentState(BaseDocumentState):
    def validate_notice_document_already_exists(self, doc_data):
        if tender_created_after(NOTICE_DOC_REQUIRED_FROM):
            tender_docs = deepcopy(get_tender().get("documents", []))
            new_documents = self.request.validated["data"]
            if isinstance(new_documents, list):  # POST (array of docs)
                tender_docs.extend(new_documents)
            else:  # PATCH/PUT
                tender_docs.append(doc_data)
            validate_doc_type_quantity(tender_docs)

    def document_always(self, data: dict) -> None:
        self.validate_notice_document_already_exists(data)
        if data.get("documentType") != "notice":
            self.validate_action_with_exist_inspector_review_request()
        super().document_always(data)
