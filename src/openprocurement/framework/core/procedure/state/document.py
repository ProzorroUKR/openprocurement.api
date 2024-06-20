from openprocurement.api.procedure.context import get_qualification
from openprocurement.api.utils import raise_operation_error
from openprocurement.framework.core.procedure.state.framework import FrameworkState
from openprocurement.framework.core.procedure.state.milestone import MilestoneState
from openprocurement.framework.core.procedure.state.qualification import (
    QualificationState,
)
from openprocurement.framework.core.procedure.state.submission import SubmissionState
from openprocurement.framework.core.procedure.validation import (
    validate_evaluation_reports_doc_quantity,
)
from openprocurement.tender.core.procedure.state.document import BaseDocumentStateMixing


class BaseFrameworkDocumentState(BaseDocumentStateMixing, FrameworkState):
    item_name = "framework"


class SubmissionDocumentState(BaseDocumentStateMixing, SubmissionState):
    item_name = "submission"


class QualificationDocumentState(BaseDocumentStateMixing, QualificationState):
    item_name = "qualification"

    def validate_evaluation_report_document_already_exists(self, doc_data):
        if doc_data.get("documentType") == "evaluationReports":
            qualification = get_qualification()
            for doc in qualification.get("documents", []):
                if doc.get("documentType") == "evaluationReports" and doc["id"] != doc_data.get("id"):
                    raise_operation_error(
                        self.request,
                        "evaluationReports document already exists in qualification",
                        name="documents",
                        status=422,
                    )
        documents = self.request.validated["data"]
        if isinstance(documents, list) and len(documents) > 1:
            validate_evaluation_reports_doc_quantity(self.request, documents)

    def document_always(self, data):
        self.validate_evaluation_report_document_already_exists(data)


class MilestoneDocumentState(BaseDocumentStateMixing, MilestoneState):
    item_name = "milestone"
