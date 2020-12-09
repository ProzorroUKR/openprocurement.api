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
)
from openprocurement.framework.electroniccatalogue.models import Qualification


@submissionsresource(
    name="electronicCatalogue:Submission",
    path="/submissions/{submission_id}",
    submissionType="electronicCatalogue",
    description="",  # TODO: add description
)
class SubmissionResource(APIResource):
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
        old_status = submission.status
        new_status = self.request.validated["data"].get("status", old_status)

        now = get_now()
        if new_status != old_status:
            submission.date = now

        activated = new_status == "active" and old_status != new_status
        if activated:
            submission.datePublished = now
            self.create_qualification()

        apply_patch(self.request, src=self.request.validated["submission_src"], obj_name="submission")

        self.LOGGER.info("Updated submission {}".format(submission.id),
                         extra=context_unpack(self.request, {"MESSAGE_ID": "submission_patch"}))

        return {"data": submission.serialize("view")}

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

        if save_qualification(self.request):
            submission.qualificationID = qualification_id
            self.LOGGER.info(
                "Created qualification {}".format(qualification_id),
                extra=context_unpack(
                    self.request,
                    {"MESSAGE_ID": "qualification_create"},
                    {"qualification_id": qualification_id,
                     "qualification_mode": qualification.mode},
                ),
            )
