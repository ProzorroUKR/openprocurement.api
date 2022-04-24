from openprocurement.api.constants import FAST_CATALOGUE_FLOW_FRAMEWORK_IDS
from openprocurement.api.utils import APIResource, json_view, context_unpack, get_now, generate_id
from openprocurement.framework.core.utils import (
    submissionsresource,
    apply_patch,
    save_qualification,
)
from openprocurement.framework.core.validation import (
    validate_patch_submission_data,
    validate_operation_submission_in_not_allowed_period,
    validate_submission_status,
    validate_update_submission_in_not_allowed_status,
    validate_activate_submission,
    validate_action_in_not_allowed_framework_status,
)
from openprocurement.framework.electroniccatalogue.models import Qualification
from openprocurement.framework.electroniccatalogue.views.agreement import AgreementMixin


@submissionsresource(
    name="electronicCatalogue:Submissions",
    path="/submissions/{submission_id}",
    submissionType="electronicCatalogue",
    description="",  # TODO: add description
)
class SubmissionResource(APIResource, AgreementMixin):
    @json_view(permission="view_submission")
    def get(self):
        """
        Get info by submission
        """
        submission_data = self.context.serialize("view")
        return {"data": submission_data}

    @json_view(
        content_type="application/json",
        validators=(
            validate_patch_submission_data,
            validate_operation_submission_in_not_allowed_period,
            validate_update_submission_in_not_allowed_status,
            validate_action_in_not_allowed_framework_status("submission"),
            validate_submission_status,
            validate_activate_submission,
        ),
        permission="edit_submission",
    )
    def patch(self):
        """
        Submission edit(partial)
        """
        submission = self.request.context
        framework = self.request.validated["framework"]
        old_status = submission.status
        new_status = self.request.validated["data"].get("status", old_status)

        now = get_now()
        if new_status != old_status:
            submission.date = now

        activated = new_status == "active" and old_status != new_status
        if activated:
            submission.datePublished = now
            self.create_qualification()

        apply_patch(
            self.request,
            src=self.request.validated["submission_src"],
            obj_name="submission"
        )

        self.LOGGER.info(
            "Updated submission {}".format(submission.id),
            extra=context_unpack(self.request, {"MESSAGE_ID": "submission_patch"})
        )

        data = submission.serialize("view")

        if activated and submission.frameworkID in FAST_CATALOGUE_FLOW_FRAMEWORK_IDS:
            self.activate_qualification()
            self.ensure_agreement()
            self.create_agreement_contract()
            self.request.validated["data"]["status"] = "complete"

            apply_patch(
                self.request,
                src=self.request.validated["submission_src"],
                obj_name="submission"
            )

            self.LOGGER.info(
                "Updated submission {}".format(submission.id),
                extra=context_unpack(self.request, {"MESSAGE_ID": "submission_patch"})
            )

        return {"data": data}

    def create_qualification(self):
        submission = self.request.context
        framework = self.request.validated["framework"]

        qualification_id = generate_id()
        qualification_data = {
            "id": qualification_id,
            "frameworkID": framework["_id"],
            "submissionID": submission.id,
            "framework_owner": framework["owner"],
            "framework_token": framework["owner_token"],
            "qualificationType": framework["frameworkType"],
            "mode": framework.get("type")
        }
        qualification = Qualification(qualification_data)
        self.request.validated["qualification_src"] = {}
        self.request.validated["qualification"] = qualification

        if save_qualification(self.request, insert=True):
            submission.qualificationID = qualification_id
            self.LOGGER.info(
                "Created qualification {}".format(qualification_id),
                extra=context_unpack(
                    self.request,
                    {"MESSAGE_ID": "qualification_create"},
                    {
                        "qualification_id": qualification_id,
                        "qualification_mode": qualification.mode
                    },
                ),
            )

    def activate_qualification(self):
        qualification = self.request.validated["qualification"]
        self.request.validated["qualification_src"] = qualification.serialize("plain")
        qualification.status = "active"
        self.request.validated["qualification"] = qualification
        apply_patch(
            self.request,
            src=self.request.validated["qualification_src"],
            data=qualification,
            obj_name="qualification"
        )
        self.LOGGER.info(
            "Updated qualification {}".format(qualification.id),
            extra=context_unpack(self.request, {"MESSAGE_ID": "qualification_patch"})
        )

