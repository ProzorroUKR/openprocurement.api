from logging import getLogger

from openprocurement.api.constants import FAST_CATALOGUE_FLOW_FRAMEWORK_IDS
from openprocurement.api.context import get_now, get_request
from openprocurement.api.procedure.context import get_object
from openprocurement.api.procedure.state.base import BaseState, ConfigMixin
from openprocurement.api.utils import raise_operation_error
from openprocurement.framework.dps.constants import DPS_TYPE

LOGGER = getLogger(__name__)


class SubmissionConfigMixin(ConfigMixin):
    default_config_schema = {
        "type": "object",
        "properties": {
            "test": {"type": "boolean"},
            "restricted": {"type": "boolean"},
        },
    }

    def validate_config(self, data):
        super().validate_config(data)

        # custom validations
        self.validate_restricted_config(data)

    def validate_restricted_config(self, data):
        config = data["config"]
        value = config.get("restricted")

        if data.get("frameworkType") == DPS_TYPE:
            if value is None:
                raise_operation_error(
                    self.request, ["restricted is required for this framework type"], status=422, name="restricted"
                )
            if data.get("procuringEntity", {}).get("kind") == "defense":
                if value is False:
                    raise_operation_error(
                        self.request,
                        ["restricted must be true for defense procuring entity"],
                        status=422,
                        name="restricted",
                    )
            else:
                if value is True:
                    raise_operation_error(
                        self.request,
                        ["restricted must be false for non-defense procuring entity"],
                        status=422,
                        name="restricted",
                    )
        else:
            if value is True:
                raise_operation_error(
                    self.request, ["restricted must be false for this framework type"], status=422, name="restricted"
                )


class SubmissionState(BaseState, SubmissionConfigMixin):
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
        data["mode"] = framework.get("mode")
        data["framework_owner"] = framework["owner"]
        data["framework_token"] = framework["owner_token"]
        if get_request().json["data"].get("status") == "draft":
            data["status"] = "draft"
        if framework["config"].get("test", False):
            data["config"]["test"] = framework["config"]["test"]
        data["config"]["restricted"] = framework["config"]["restrictedDerivatives"]
