from logging import getLogger

from openprocurement.api.context import get_now
from openprocurement.api.procedure.context import get_framework
from openprocurement.api.procedure.state.base import BaseState
from openprocurement.api.utils import (
    generate_id,
    raise_operation_error,
    request_init_qualification,
)
from openprocurement.framework.core.procedure.state.chronograph import (
    ChronographEventsMixing,
)
from openprocurement.tender.core.procedure.validation import validate_doc_type_quantity

LOGGER = getLogger(__name__)


class QualificationState(ChronographEventsMixing, BaseState):
    def __init__(self, request, framework=None):
        super().__init__(request)
        self.framework = framework

    def status_up(self, before, after, data):
        super().status_up(before, after, data)

    def on_patch(self, before, after):
        if self.status_changed(before, after):
            after["date"] = get_now().isoformat()
        super().on_patch(before, after)

        if len(before.get("documents", [])) != len(after.get("documents", [])):
            validate_doc_type_quantity(after["documents"], document_type="evaluationReports", obj_name="qualification")

        if before.get("status") != after.get("status"):
            self.framework.submission.set_complete_status()

        if before["status"] == "pending" and after.get("status") == "active":
            self.validate_evaluation_report_doc_required(after)
            self.on_set_active()

    def validate_evaluation_report_doc_required(self, qualification):
        for doc in qualification.get("documents", []):
            if doc.get("documentType") == "evaluationReports" and doc["title"][-4:] == ".p7s":
                break
        else:
            raise_operation_error(
                self.request,
                "Document with type 'evaluationReports' and format pkcs7-signature is required",
                status=422,
                name="documents",
            )

    def set_active_status(self):
        """
        POST submission in FAST_CATALOGUE_FLOW_FRAMEWORK_IDS
        """
        self.request.validated["qualification"]["status"] = "active"
        self.on_set_active()

    def on_set_active(self):
        """
        This method is called when qualification changes its status to "active"
        it can be done by PATCH qualification or POST submission in FAST_CATALOGUE_FLOW_FRAMEWORK_IDS
        """
        agreement_state = self.framework.agreement
        agreement_state.create_agreement_if_not_exist()
        agreement_state.create_agreement_contract()
        agreement_state.update_next_check(self.request.validated.get("agreement"))

    def status_changed(self, before, after):
        old_status = before["status"]
        new_status = after.get("status", old_status)
        return new_status != old_status

    def create_from_submission(self, data):
        """
        This method creates qualification
        when submission is activated
        """
        request = self.request
        framework = get_framework()

        qualification = {
            "_id": generate_id(),
            "frameworkID": framework["_id"],
            "submissionID": data["_id"],
            "framework_owner": framework["owner"],
            "framework_token": framework["owner_token"],
            "submission_owner": data["owner"],
            "submission_token": data["owner_token"],
            "qualificationType": framework["frameworkType"],
            "mode": framework.get("mode"),
            "status": "pending",
            "date": get_now().isoformat(),
            "config": {
                "test": framework["config"].get("test", False),
                "restricted": framework["config"].get("restrictedDerivatives", False),
            },
        }

        request_init_qualification(request, qualification, qualification_src={})

        return qualification
