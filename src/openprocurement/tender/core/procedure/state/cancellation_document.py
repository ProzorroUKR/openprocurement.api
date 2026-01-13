from copy import deepcopy

from openprocurement.api.constants_env import CANCELLATION_REPORT_DOC_REQUIRED_FROM
from openprocurement.api.procedure.context import get_tender
from openprocurement.api.utils import raise_operation_error
from openprocurement.api.validation import OPERATIONS
from openprocurement.tender.core.procedure.context import get_cancellation, get_request
from openprocurement.tender.core.procedure.state.cancellation import (
    CancellationStateMixing,
)
from openprocurement.tender.core.procedure.state.document import BaseDocumentStateMixing
from openprocurement.tender.core.procedure.state.tender import TenderState
from openprocurement.tender.core.procedure.utils import (
    tender_created_after,
    tender_created_after_2020_rules,
)
from openprocurement.tender.core.procedure.validation import validate_doc_type_quantity


class CancellationDocumentStateMixing(BaseDocumentStateMixing, CancellationStateMixing):
    def document_always(self, data):
        self.validate_confidentiality(data)
        self.validate_sign_documents_already_exists(data)

    @staticmethod
    def validate_cancellation_document_allowed(request, _, cancellation):
        if tender_created_after_2020_rules():
            status = cancellation["status"]
            if status == "draft":
                pass
            elif status == "pending" and any(
                i.get("status") == "satisfied" for i in cancellation.get("complaints", "")
            ):
                raise_operation_error(
                    request,
                    f"Document can't be {OPERATIONS.get(request.method)} in current({status}) cancellation status",
                )

    def validate_document_post(self, data):
        request, tender, cancellation = get_request(), get_tender(), get_cancellation()
        self.validate_cancellation_in_allowed_tender_status(request, tender, cancellation)
        self.validate_cancellation_document_allowed(request, tender, cancellation)
        self.validate_pending_cancellation_present(request, tender, cancellation)

    def validate_document_patch(self, before, after):
        request, tender, cancellation = get_request(), get_tender(), get_cancellation()
        self.validate_cancellation_in_allowed_tender_status(request, tender, cancellation)
        self.validate_cancellation_document_allowed(request, tender, cancellation)
        self.validate_pending_cancellation_present(request, tender, cancellation)

    def validate_sign_documents_already_exists(self, doc_data):
        cancellation_docs = deepcopy(get_cancellation().get("documents", []))
        new_documents = self.request.validated["data"]
        if isinstance(new_documents, list):  # POST (array of docs)
            cancellation_docs.extend(new_documents)
        else:  # PATCH/PUT
            cancellation_docs.append(doc_data)
        if tender_created_after(CANCELLATION_REPORT_DOC_REQUIRED_FROM):
            validate_doc_type_quantity(cancellation_docs, document_type="cancellationReport")


class CancellationDocumentState(CancellationDocumentStateMixing, TenderState):
    pass
