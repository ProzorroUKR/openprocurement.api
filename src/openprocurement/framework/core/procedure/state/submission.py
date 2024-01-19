from logging import getLogger
from openprocurement.api.constants import FAST_CATALOGUE_FLOW_FRAMEWORK_IDS
from openprocurement.api.context import get_now, get_request
from openprocurement.api.procedure.context import get_object
from openprocurement.api.procedure.state.base import BaseState

LOGGER = getLogger(__name__)


class SubmissionState(BaseState):

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
            after["qualificationID"] = qualification['_id']
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
        data["config"] = {
            "test": framework["config"].get("test", False),
            "restricted": framework["config"]["restrictedDerivatives"],
        }
