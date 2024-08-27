from datetime import timedelta
from logging import getLogger

from openprocurement.api.context import get_now
from openprocurement.api.procedure.context import get_framework
from openprocurement.api.procedure.state.base import BaseState
from openprocurement.api.utils import (
    calculate_full_date,
    generate_id,
    request_init_qualification,
)
from openprocurement.framework.core.procedure.state.chronograph import (
    ChronographEventsMixing,
)
from openprocurement.tender.core.procedure.validation import (
    validate_doc_type_quantity,
    validate_doc_type_required,
)

LOGGER = getLogger(__name__)


class QualificationState(ChronographEventsMixing, BaseState):
    working_days = True

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
            start_date = get_now()
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
            "date": get_now().isoformat(),
            "config": {
                "test": framework["config"].get("test", False),
                "restricted": framework["config"]["restrictedDerivatives"],
                "qualificationComplainDuration": framework["config"]["qualificationComplainDuration"],
            },
        }

        request_init_qualification(request, qualification, qualification_src={})

        return qualification
