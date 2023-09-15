from copy import deepcopy
from logging import getLogger

from openprocurement.api.constants import FAST_CATALOGUE_FLOW_FRAMEWORK_IDS
from openprocurement.api.context import get_now, get_request
from openprocurement.api.utils import context_unpack

from openprocurement.framework.core.procedure.context import get_object, get_object_config
from openprocurement.framework.core.procedure.models.qualification import CreateQualification
from openprocurement.framework.core.procedure.models.submission import Submission
from openprocurement.framework.core.procedure.state.agreement import AgreementStateMixin
from openprocurement.framework.core.procedure.utils import save_object
from openprocurement.framework.core.utils import get_submission_by_id
from openprocurement.tender.core.procedure.state.base import BaseState


LOGGER = getLogger(__name__)


class QualificationState(AgreementStateMixin, BaseState):
    submission_model = Submission

    def status_up(self, before, after, data):
        super().status_up(before, after, data)

    def on_patch(self, before, after):
        if self.status_changed(before, after):
            after["date"] = get_now().isoformat()
        super().on_patch(before, after)

    def status_changed(self, before, after):
        old_status = before["status"]
        new_status = after.get("status", old_status)
        return new_status != old_status

    def after_patch(self, before, after):
        if self.status_changed(before, after):
            self.complete_submission(after)
        if before["status"] == "pending" and after.get("status") == "active":
            self.get_or_create_agreement()
            self.create_agreement_contract()

    def complete_submission(self, after):
        submission_data = get_submission_by_id(self.request, after["submissionID"])
        get_request().validated["submission_src"] = deepcopy(submission_data)
        submission_data["status"] = "complete"
        submission = self.submission_model(submission_data)
        get_request().validated["submission"] = submission.serialize()
        if save_object(self.request, "submission"):
            LOGGER.info(
                f"Updated submission {submission.id}",
                extra=context_unpack(self.request, {"MESSAGE_ID": "submission_patch"}),
            )
