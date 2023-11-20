from copy import deepcopy
from logging import getLogger

from openprocurement.api.constants import FAST_CATALOGUE_FLOW_FRAMEWORK_IDS
from openprocurement.api.context import get_now, get_request
from openprocurement.api.utils import context_unpack

from openprocurement.framework.core.procedure.context import get_object, get_object_config
from openprocurement.framework.core.procedure.models.qualification import CreateQualification
from openprocurement.framework.core.procedure.state.agreement import AgreementStateMixin
from openprocurement.framework.core.procedure.utils import save_object
from openprocurement.tender.core.procedure.state.base import BaseState


LOGGER = getLogger(__name__)


class SubmissionState(AgreementStateMixin, BaseState):
    qualification_model = CreateQualification

    def on_post(self, data):
        data["date"] = get_now().isoformat()
        self.set_submission_data(data)
        super().on_post(data)

    def on_patch(self, before, after):
        if self.status_changed(before, after):
            after["date"] = get_now().isoformat()
        if self.submission_activated(before, after):
            after["datePublished"] = get_now().isoformat()
            self.create_qualification(after)
        super().on_patch(before, after)

    def status_changed(self, before, after):
        old_status = before["status"]
        new_status = after.get("status", old_status)
        return new_status != old_status

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

    def after_patch(self, before, after):
        if self.submission_activated(before, after) and before["frameworkID"] in FAST_CATALOGUE_FLOW_FRAMEWORK_IDS:
            self.activate_qualification()
            self.get_or_create_agreement()
            self.create_agreement_contract()
            after["status"] = "complete"
            save_object(self.request, "submission")
            LOGGER.info(
                f"Updated submission {after['_id']}",
                extra=context_unpack(self.request, {"MESSAGE_ID": "submission_patch"})
            )

    def create_qualification(self, data):
        framework = get_object("framework")
        framework_config = get_object_config("framework")

        qualification_data = {
            "frameworkID": framework["_id"],
            "submissionID": data["_id"],
            "framework_owner": framework["owner"],
            "framework_token": framework["owner_token"],
            "submission_owner": data["owner"],
            "submission_token": data["owner_token"],
            "qualificationType": framework["frameworkType"],
            "mode": framework.get("mode")
        }
        qualification_config = {}
        if framework_config.get("test", False):
            qualification_config["test"] = framework_config["test"]
        if framework_config.get("restrictedDerivatives", False):
            qualification_config["restricted"] = True

        qualification = self.qualification_model(qualification_data).serialize()
        get_request().validated["qualification_src"] = {}
        get_request().validated["qualification"] = qualification
        get_request().validated["qualification_config"] = qualification_config

        if save_object(get_request(), "qualification", insert=True):
            data["qualificationID"] = qualification['_id']
            LOGGER.info(
                f"Created qualification {qualification['_id']}",
                extra=context_unpack(
                    get_request(),
                    {"MESSAGE_ID": "qualification_create"},
                    {
                        "qualification_id": qualification['_id'],
                        "qualification_mode": qualification.get('mode')
                    },
                ),
            )

    def activate_qualification(self):
        qualification = get_request().validated["qualification"]
        get_request().validated["qualification_src"] = deepcopy(qualification)
        qualification["status"] = "active"
        get_request().validated["qualification"] = qualification
        if save_object(self.request, "qualification"):
            LOGGER.info(
                f"Updated qualification {qualification['_id']}",
                extra=context_unpack(self.request, {"MESSAGE_ID": "qualification_patch"})
            )
