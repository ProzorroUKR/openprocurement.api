from copy import deepcopy

from openprocurement.api.constants_env import (
    EVALUATION_REPORTS_DOC_REQUIRED_FROM,
    NOTICE_DOC_REQUIRED_FROM,
)
from openprocurement.api.procedure.context import get_tender
from openprocurement.api.utils import raise_operation_error
from openprocurement.tender.core.procedure.state.document import BaseDocumentState
from openprocurement.tender.core.procedure.utils import tender_created_after
from openprocurement.tender.core.procedure.validation import validate_doc_type_quantity


class TenderDocumentState(BaseDocumentState):
    allow_deletion = True
    deletion_allowed_statuses = ("draft", "draft.stage2")

    def validate_sign_documents_already_exists(self, doc_data):
        tender_docs = deepcopy(get_tender().get("documents", []))
        new_documents = self.request.validated["data"]
        if isinstance(new_documents, list):  # POST (array of docs)
            tender_docs.extend(new_documents)
        else:  # PATCH/PUT
            tender_docs.append(doc_data)
        if tender_created_after(NOTICE_DOC_REQUIRED_FROM):
            validate_doc_type_quantity(tender_docs)
        if tender_created_after(EVALUATION_REPORTS_DOC_REQUIRED_FROM):
            validate_doc_type_quantity(tender_docs, document_type="evaluationReports")

    def document_always(self, data: dict) -> None:
        self.validate_sign_documents_already_exists(data)
        if data.get("documentType") != "notice":
            self.validate_action_with_exist_inspector_review_request()
        self.validate_contract_proforma_document(data)
        super().document_always(data)

    def validate_contract_proforma_document(self, data: dict) -> None:
        if data.get("documentType") != "contractProforma":
            return

        tender = self.request.validated["tender"]
        if tender.get("contractTemplateName"):
            raise_operation_error(
                self.request,
                "Cannot use both contractTemplateName and contractProforma document simultaneously",
                status=422,
            )
