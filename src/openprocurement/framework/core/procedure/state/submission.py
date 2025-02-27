from logging import getLogger

from openprocurement.api.constants_env import FAST_CATALOGUE_FLOW_FRAMEWORK_IDS
from openprocurement.api.context import get_now, get_request
from openprocurement.api.procedure.context import get_object
from openprocurement.api.procedure.state.base import BaseState, ConfigMixin
from openprocurement.api.utils import raise_operation_error

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
    def __init__(self, request, framework=None):
        super().__init__(request)
        self.framework = framework

    def on_post(self, data):
        data["date"] = get_now().isoformat()
        self.set_submission_data(data)
        super().on_post(data)

    def on_patch(self, before, after):
        super().on_patch(before, after)

        if self.status_changed(before, after):
            after["date"] = get_now().isoformat()
        if self.submission_activated(before, after):
            qualification = self.framework.qualification.create_from_submission(after)
            after["qualificationID"] = qualification["_id"]
            after["datePublished"] = get_now().isoformat()

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
