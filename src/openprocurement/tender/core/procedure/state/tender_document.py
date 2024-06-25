from openprocurement.api.constants import NOTICE_DOC_REQUIRED_FROM
from openprocurement.api.context import get_request
from openprocurement.api.procedure.context import get_tender
from openprocurement.api.utils import raise_operation_error
from openprocurement.tender.core.procedure.state.document import BaseDocumentState
from openprocurement.tender.core.procedure.utils import tender_created_after
from openprocurement.tender.core.procedure.validation import (
    validate_notice_doc_quantity,
)


class TenderDocumentState(BaseDocumentState):
    def validate_notice_document_already_exists(self, doc_data):
        if tender_created_after(NOTICE_DOC_REQUIRED_FROM):
            if doc_data.get("documentType") == "notice":
                tender = get_tender()
                for doc in tender.get("documents", []):
                    if doc.get("documentType") == "notice" and doc["id"] != doc_data.get("id"):
                        raise_operation_error(
                            get_request(),
                            "Notice document already exists in tender",
                            name="documents",
                            status=422,
                        )
            documents = self.request.validated["data"]
            if isinstance(documents, list) and len(documents) > 1:
                validate_notice_doc_quantity(documents)

    def document_always(self, data: dict) -> None:
        self.validate_notice_document_already_exists(data)
        if data.get("documentType") != "notice":
            self.validate_action_with_exist_inspector_review_request()
        super().document_always(data)
