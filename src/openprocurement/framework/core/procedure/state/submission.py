from logging import getLogger

from openprocurement.api.constants_env import FAST_CATALOGUE_FLOW_FRAMEWORK_IDS
from openprocurement.api.context import get_request, get_request_now
from openprocurement.api.procedure.context import get_object
from openprocurement.api.procedure.state.base import BaseState, ConfigMixin
from openprocurement.api.utils import (
    get_agreement_by_id,
    get_framework_by_id,
    raise_operation_error,
    request_init_framework,
)
from openprocurement.api.validation import OPERATIONS
from openprocurement.framework.core.procedure.models.submission import PatchSubmission
from openprocurement.tender.core.procedure.utils import dt_from_iso

LOGGER = getLogger(__name__)


class SubmissionConfigMixin(ConfigMixin):
    default_config_schema = {
        "type": "object",
        "properties": {
            "restricted": {"type": "boolean"},
        },
    }

    def on_post(self, data):
        self.validate_config(data)
        self.validate_restricted_config(data)
        super().on_post(data)

    def validate_restricted_config(self, data):
        framework = get_object("framework")
        restricted = data["config"].get("restricted")
        restricted_derivatives = framework["config"]["restrictedDerivatives"]
        if restricted_derivatives is True and restricted is False:
            raise_operation_error(
                self.request,
                ["restricted must be true for framework with restrictedDerivatives true"],
                status=422,
                name="config.restricted",
            )
        elif restricted_derivatives is False and restricted is True:
            raise_operation_error(
                self.request,
                ["restricted must be false for framework with restrictedDerivatives false"],
                status=422,
                name="config.restricted",
            )


class SubmissionState(SubmissionConfigMixin, BaseState):
    # post_data_model / data_model: the submission models of the procedure
    patch_data_model = PatchSubmission

    # roles that may update a submission without being its owner
    submission_patch_owner_exempt_roles: tuple = ("Administrator",)
    # submission status changes allowed by its owner
    submission_status_changes: dict = {"draft": ("draft", "active", "deleted")}

    def __init__(self, request, framework=None):
        super().__init__(request)
        self.framework = framework

    # --- request validation (called from the views) ---

    def validate_submission_post_request(self):
        self.validate_input_data(self.get_post_data_model())
        self.validate_submission_framework_id()
        self.validate_config_data()
        self.validate_submission_period()
        self.validate_submission_framework_status()
        self.validate_submission_contract_not_active()
        self.validate_data_documents(route_key="submission_id")

    def validate_submission_patch_request(self):
        if self.request.authenticated_role not in self.submission_patch_owner_exempt_roles:
            self.validate_item_owner("submission")
        self.validate_patch_input_data(self.get_patch_data_model())
        self.fetch_submission_framework()
        self.validate_submission_update_allowed()
        self.validate_submission_status_change()
        self.validate_submission_activation()
        self.validate_submission_period()
        self.validate_submission_framework_status()
        self.validate_patch_data(self.get_data_model(), item_name="submission")

    def validate_submission_framework_id(self):
        """the framework of the posted submission must exist (request.validated["framework"])"""
        framework = get_framework_by_id(self.request, self.request.validated["data"]["frameworkID"], raise_error=False)
        if not framework:
            raise_operation_error(
                self.request,
                ["frameworkID must be one of exists frameworks"],
                status=422,
                name="frameworkID",
            )
        request_init_framework(self.request, framework)

    def fetch_submission_framework(self):
        """the framework of the updated submission (request.validated["framework"])"""
        request = self.request
        framework_id = request.validated["data"].get("frameworkID", request.validated["submission"]["frameworkID"])
        request_init_framework(request, get_framework_by_id(request, framework_id))

    def validate_submission_period(self):
        framework = self.request.validated["framework"]
        operation = OPERATIONS.get(self.request.method)
        period = framework.get("period")
        if not period or "startDate" not in period or "endDate" not in period:
            raise_operation_error(self.request, f"Submission cannot be {operation} without framework period")
        period_start_date = dt_from_iso(period["startDate"])
        period_end_date = dt_from_iso(period["endDate"])
        now = get_request_now()
        if now < period_start_date or now > period_end_date:
            raise_operation_error(
                self.request,
                f"Submission can be {operation} only during the period: from ({period_start_date}) to ({period_end_date}).",
            )

    def validate_submission_framework_status(self):
        framework_status = self.request.validated["framework"].get("status", "")
        if framework_status != "active":
            raise_operation_error(
                self.request,
                f"Can't {OPERATIONS.get(self.request.method)} submission in current ({framework_status}) framework status",
            )

    def validate_submission_contract_not_active(self):
        """a submission can't be added while the agreement has an active / suspended contract of the same tenderer"""
        request = self.request
        framework = request.validated["framework"]
        agreement = get_agreement_by_id(request, framework.get("agreementID"), raise_error=False)
        if not agreement:
            return
        identifier_id = request.validated["data"]["tenderers"][0]["identifier"]["id"]
        for contract in agreement["contracts"]:
            if contract["suppliers"][0]["identifier"]["id"] == identifier_id:
                if contract["status"] in ("active", "suspended"):
                    raise_operation_error(
                        request,
                        f"Can't add submission when contract in "
                        f"agreement with same identifier.id in {contract['status']} status",
                    )
                break

    def validate_submission_update_allowed(self):
        status = self.request.validated["submission_src"]["status"]
        if status in ("deleted", "active", "complete"):
            raise_operation_error(self.request, f"Can't update submission in current ({status}) status")

    def validate_submission_status_change(self):
        curr_status = self.request.validated["submission_src"]["status"]
        new_status = self.request.validated["data"].get("status", curr_status)
        if new_status not in self.submission_status_changes.get(curr_status, ()):
            raise_operation_error(
                self.request,
                f"Can't update submission from current ({curr_status}) to new ({new_status}) status",
            )

    def validate_submission_activation(self):
        request = self.request
        submission = request.validated["submission"]
        old_status = submission["status"]
        new_status = request.validated["data"].get("status", old_status)
        if new_status != "active" or old_status == new_status:
            return
        framework_id = submission["frameworkID"]
        identifier_id = submission["tenderers"][0]["identifier"]["id"]
        if request.registry.mongodb.submissions.count_active_submissions_by_framework_id(framework_id, identifier_id):
            raise_operation_error(request, f"Tenderer already have active submission for framework {framework_id}")
        if request.registry.mongodb.agreements.has_active_suspended_contracts(framework_id, identifier_id):
            raise_operation_error(
                request,
                f"Tenderer can't activate submission with active/suspended contract in agreement "
                f"for framework {framework_id}",
            )

    def on_post(self, data):
        data["date"] = get_request_now().isoformat()
        self.set_submission_data(data)
        super().on_post(data)

    def on_patch(self, before, after):
        super().on_patch(before, after)

        if self.status_changed(before, after):
            after["date"] = get_request_now().isoformat()
        if self.submission_activated(before, after):
            qualification = self.framework.qualification.create_from_submission(after)
            after["qualificationID"] = qualification["_id"]
            after["datePublished"] = get_request_now().isoformat()

            if before["frameworkID"] in FAST_CATALOGUE_FLOW_FRAMEWORK_IDS:
                self.framework.qualification.set_active_status()
                after["status"] = "complete"

    @staticmethod
    def status_changed(before, after):
        old_status = before["status"]
        new_status = after.get("status", old_status)
        return new_status != old_status

    def set_complete_status(self):
        self.request.validated["submission"]["status"] = "complete"

    def submission_activated(self, before, after):
        return after.get("status") == "active" and self.status_changed(before, after)

    def set_submission_data(self, data):
        framework = get_object("framework")
        data["submissionType"] = framework["frameworkType"]
        data["framework_owner"] = framework["owner"]
        data["framework_token"] = framework["owner_token"]
        data["mode"] = framework.get("mode")
        if get_request().json["data"].get("status") == "draft":
            data["status"] = "draft"
