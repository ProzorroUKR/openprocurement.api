from copy import deepcopy

from openprocurement.api.procedure.context import get_qualification
from openprocurement.framework.core.procedure.state.framework import FrameworkState
from openprocurement.framework.core.procedure.state.milestone import MilestoneState
from openprocurement.framework.core.procedure.state.qualification import (
    QualificationState,
)
from openprocurement.framework.core.procedure.state.submission import SubmissionState
from openprocurement.tender.core.procedure.state.document import BaseDocumentStateMixing
from openprocurement.tender.core.procedure.validation import validate_doc_type_quantity


class BaseFrameworkDocumentState(BaseDocumentStateMixing, FrameworkState):
    item_name = "framework"


class SubmissionDocumentState(BaseDocumentStateMixing, SubmissionState):
    item_name = "submission"


class QualificationDocumentState(BaseDocumentStateMixing, QualificationState):
    item_name = "qualification"

    def validate_evaluation_report_document_already_exists(self, doc_data):
        qualification_docs = deepcopy(get_qualification().get("documents", []))
        new_documents = self.request.validated["data"]
        if isinstance(new_documents, list):  # POST (array of docs)
            qualification_docs.extend(new_documents)
        else:  # PATCH/PUT
            qualification_docs.append(doc_data)
        validate_doc_type_quantity(qualification_docs, document_type="evaluationReports", obj_name="qualification")

    def document_always(self, data):
        self.validate_evaluation_report_document_already_exists(data)


class MilestoneDocumentState(BaseDocumentStateMixing, MilestoneState):
    item_name = "milestone"
