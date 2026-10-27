from datetime import timedelta
from logging import getLogger

from openprocurement.api.context import get_request_now
from openprocurement.api.procedure.context import get_framework
from openprocurement.api.procedure.state.base import BaseState
from openprocurement.api.utils import (
    calculate_full_date,
    generate_id,
    raise_operation_error,
    request_init_qualification,
)
from openprocurement.api.validation import OPERATIONS
from openprocurement.framework.core.procedure.models.qualification import PatchQualification
from openprocurement.framework.core.procedure.state.chronograph import (
    FrameworkChronographEventsMixing,
)
from openprocurement.framework.core.procedure.utils import is_framework_owner
from openprocurement.tender.core.procedure.validation import (
    validate_doc_type_quantity,
    validate_doc_type_required,
)

LOGGER = getLogger(__name__)


class QualificationState(FrameworkChronographEventsMixing, BaseState):
    # data_model: the qualification model of the procedure
    patch_data_model = PatchQualification

    working_days = True
    evaluation_reports_doc_required = True

    def __init__(self, request, framework=None):
        super().__init__(request)
        self.framework = framework

    # --- request validation (called from the views) ---

    def validate_qualification_patch_request(self):
        if self.request.authenticated_role != "Administrator":
            self.validate_qualification_framework_owner()
        self.validate_patch_input_data(self.get_patch_data_model())
        self.validate_qualification_update_allowed()
        self.validate_qualification_framework_status()
        self.validate_patch_data(self.get_data_model(), item_name="qualification")

    def validate_qualification_framework_owner(self):
        if not is_framework_owner(self.request, self.request.validated["qualification"]):
            raise_operation_error(self.request, "Forbidden", location="url", name="permission")

    def validate_qualification_update_allowed(self):
        status = self.request.validated["qualification_src"]["status"]
        if status in ("unsuccessful", "active"):
            raise_operation_error(self.request, f"Can't update qualification in current ({status}) status")

    def validate_qualification_framework_status(self):
        framework_status = self.request.validated["framework"].get("status", "")
        if framework_status != "active":
            raise_operation_error(
                self.request,
                f"Can't {OPERATIONS.get(self.request.method)} qualification in current ({framework_status}) framework status",
            )

    def status_up(self, before, after, data):
        super().status_up(before, after, data)

    def on_patch(self, before, after):
        if self.status_changed(before, after):
            after["date"] = get_request_now().isoformat()
        super().on_patch(before, after)

        if len(before.get("documents", [])) != len(after.get("documents", [])):
            validate_doc_type_quantity(
                after.get("documents", []),
                document_type="evaluationReports",
                obj_name="qualification",
            )

        if before.get("status") != after.get("status"):
            if self.evaluation_reports_doc_required:
                validate_doc_type_required(after.get("documents", []), document_type="evaluationReports")
            self.set_complain_period(after)
            self.framework.submission.set_complete_status()

        if before["status"] == "pending" and after.get("status") == "active":
            self.on_set_active()

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

    def set_complain_period(self, qualification):
        qualification_complain_duration = qualification["config"]["qualificationComplainDuration"]

        if qualification_complain_duration > 0:
            start_date = get_request_now()
            end_date = calculate_full_date(
                start_date,
                timedelta(days=qualification_complain_duration),
                working_days=self.working_days,
                ceil=True,
            )

            qualification["complaintPeriod"] = {
                "startDate": start_date.isoformat(),
                "endDate": end_date.isoformat(),
            }

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
            "date": get_request_now().isoformat(),
            "config": {
                "restricted": framework["config"]["restrictedDerivatives"],
                "qualificationComplainDuration": framework["config"]["qualificationComplainDuration"],
            },
        }

        request_init_qualification(request, qualification, qualification_src={})

        return qualification
