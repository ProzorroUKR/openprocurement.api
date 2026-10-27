from copy import deepcopy

from openprocurement.api.constants_env import FAST_CATALOGUE_FLOW_FRAMEWORK_IDS
from openprocurement.api.procedure.context import get_qualification
from openprocurement.api.utils import raise_operation_error
from openprocurement.api.validation import OPERATIONS
from openprocurement.framework.core.procedure.models.document import (
    Document,
    PatchDocument,
    PostDocument,
)
from openprocurement.framework.core.procedure.models.submission_document import (
    PatchSubmissionDocument,
    PostSubmissionDocument,
    SubmissionDocument,
)
from openprocurement.framework.core.procedure.state.framework import FrameworkState
from openprocurement.framework.core.procedure.state.milestone import MilestoneState
from openprocurement.framework.core.procedure.state.qualification import (
    QualificationState,
)
from openprocurement.framework.core.procedure.state.submission import SubmissionState
from openprocurement.framework.core.procedure.utils import is_framework_owner
from openprocurement.tender.core.procedure.state.document import BaseDocumentStateMixin
from openprocurement.tender.core.procedure.validation import validate_doc_type_quantity


class FrameworkDocumentStateMixin(BaseDocumentStateMixin):
    post_data_model = PostDocument
    patch_data_model = PatchDocument
    data_model = Document

    # the availability of the operation is checked before the input data is parsed
    document_operation_check_before_input = False

    # --- request validation (called from the views) ---

    def validate_document_post_request(self):
        self.validate_document_owner(self.document_post_owner_exempt_roles)
        if self.document_operation_check_before_input:
            self.validate_document_operation_allowed()
        self.validate_input_data(self.get_post_data_model(), allow_bulk=True)
        if not self.document_operation_check_before_input:
            self.validate_document_operation_allowed()

    def validate_document_put_request(self):
        self.validate_document_owner(self.document_update_owner_exempt_roles)
        if self.document_operation_check_before_input:
            self.validate_document_operation_allowed()
        self.validate_input_data(self.get_post_data_model())
        self.update_doc_fields_on_put_document()
        self.validate_upload_document()
        self.validate_data_model(self.get_data_model())
        if not self.document_operation_check_before_input:
            self.validate_document_operation_allowed()

    def validate_document_patch_request(self):
        self.validate_document_owner(self.document_update_owner_exempt_roles)
        if self.document_operation_check_before_input:
            self.validate_document_operation_allowed()
        self.validate_patch_input_data(self.get_patch_data_model())
        self.validate_patch_data_simple(self.get_data_model(), "document")
        if not self.document_operation_check_before_input:
            self.validate_document_operation_allowed()

    def validate_document_download_allowed(self):
        pass


class BaseFrameworkDocumentState(FrameworkDocumentStateMixin, FrameworkState):
    item_name = "framework"
    document_owner_item_name = "framework"

    def validate_document_operation_allowed(self):
        status = self.request.validated["framework"].get("status")
        if status not in ("draft", "active"):
            raise_operation_error(
                self.request,
                f"Can't {OPERATIONS.get(self.request.method)} document in current ({status}) framework status",
            )


class FrameworkChangeDocumentState(FrameworkDocumentStateMixin, FrameworkState):
    item_name = "change"
    document_owner_item_name = "framework"

    def validate_document_operation_allowed(self):
        status = self.request.validated["framework"].get("status", "")
        if status != "active":
            raise_operation_error(
                self.request,
                f"Can't {OPERATIONS.get(self.request.method)} change in current ({status}) framework status",
            )


class SubmissionDocumentState(FrameworkDocumentStateMixin, SubmissionState):
    post_data_model = PostSubmissionDocument
    patch_data_model = PatchSubmissionDocument
    data_model = SubmissionDocument

    item_name = "submission"
    document_owner_item_name = "submission"

    def validate_document_operation_allowed(self):
        submission = self.request.validated["submission_src"]
        if submission["frameworkID"] in FAST_CATALOGUE_FLOW_FRAMEWORK_IDS:
            not_allowed_statuses = ("deleted",)
        else:
            not_allowed_statuses = ("deleted", "complete")
        if submission["status"] in not_allowed_statuses:
            raise_operation_error(
                self.request,
                f"Can't {OPERATIONS.get(self.request.method)} document "
                f"in current ({submission['status']}) submission status",
            )

    def validate_document_download_allowed(self):
        request = self.request
        if not request.params.get("download"):
            return
        submission = request.validated["submission"]
        if (
            request.validated["document"].get("confidentiality", "") == "buyerOnly"
            and not self.is_item_owner("submission")
            and not is_framework_owner(request, submission)
        ):
            raise_operation_error(request, "Document download forbidden.")


class QualificationDocumentState(FrameworkDocumentStateMixin, QualificationState):
    item_name = "qualification"
    document_operation_check_before_input = True

    def validate_document_owner(self, exempt_roles):
        if self.request.authenticated_role not in exempt_roles:
            self.validate_qualification_framework_owner()

    def validate_document_operation_allowed(self):
        status = self.request.validated["qualification_src"]["status"]
        if status in ("unsuccessful", "active"):
            raise_operation_error(
                self.request,
                f"Can't {OPERATIONS.get(self.request.method)} document in current ({status}) qualification status",
            )

    def validate_evaluation_report_document_already_exists(self, doc_data):
        qualification_docs = deepcopy(get_qualification().get("documents", []))
        new_documents = self.request.validated["data"]
        if isinstance(new_documents, list):  # POST (array of docs)
            qualification_docs.extend(new_documents)
        else:  # PATCH/PUT
            qualification_docs.append(doc_data)
        validate_doc_type_quantity(
            qualification_docs,
            document_type="evaluationReports",
            obj_name="qualification",
        )

    def document_always(self, data):
        self.validate_evaluation_report_document_already_exists(data)


class MilestoneDocumentState(FrameworkDocumentStateMixin, MilestoneState):
    item_name = "milestone"
    document_owner_item_name = "agreement"

    def validate_document_operation_allowed(self):
        self.validate_agreement_status(obj_name="document")
        self.validate_contract_status(obj_name="document")
        self.validate_milestone_scheduled(obj_name="milestone document")
