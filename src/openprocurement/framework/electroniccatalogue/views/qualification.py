from openprocurement.api.utils import (
    APIResource, json_view, context_unpack, get_now,
)
from openprocurement.framework.core.utils import (
    qualificationsresource,
    apply_patch,
    get_submission_by_id,
)
from openprocurement.framework.core.validation import (
    validate_patch_qualification_data,
    validate_update_qualification_in_not_allowed_status,
    validate_action_in_not_allowed_framework_status,
)
from openprocurement.framework.electroniccatalogue.models import Submission
from openprocurement.framework.electroniccatalogue.views.agreement import AgreementMixin


@qualificationsresource(
    name="electronicCatalogue:Qualifications",
    path="/qualifications/{qualification_id}",
    qualificationType="electronicCatalogue",
    description="",  # TODO: add description
)
class QualificationResource(APIResource, AgreementMixin):
    @json_view(permission="view_qualification")
    def get(self):
        """
        Get info by qualification
        """
        qualification_data = self.context.serialize("view")
        return {"data": qualification_data}

    @json_view(
        content_type="application/json",
        validators=(
            validate_update_qualification_in_not_allowed_status,
            validate_patch_qualification_data,
            validate_action_in_not_allowed_framework_status("qualification"),
        ),
        permission="edit_qualification",
    )
    def patch(self):
        """
        Qualification edit(partial)
        """
        qualification = self.request.context
        old_status = qualification.status
        new_status = self.request.validated["data"].get("status", old_status)
        changed_status = old_status != new_status
        if changed_status:
            qualification.date = get_now()
        apply_patch(
            self.request,
            src=self.request.validated["qualification_src"],
            obj_name="qualification"
        )

        self.LOGGER.info(
            "Updated qualification {}".format(qualification.id),
            extra=context_unpack(self.request, {"MESSAGE_ID": "qualification_patch"})
        )

        if changed_status:
            self.complete_submission()
        if old_status == "pending" and new_status == "active":
            self.ensure_agreement()
            self.create_agreement_contract()

        return {"data": qualification.serialize("view")}

    def complete_submission(self):
        qualification = self.request.validated["qualification"]
        submission_data = get_submission_by_id(self.request, qualification.submissionID)
        submission = Submission(submission_data)
        self.request.validated["submission_src"] = submission.serialize("plain")
        submission.status = "complete"
        self.request.validated["submission"] = submission
        apply_patch(
            self.request,
            src=self.request.validated["submission_src"],
            data=submission,
            obj_name="submission"
        )
        self.LOGGER.info(
            "Updated submission {}".format(submission.id),
            extra=context_unpack(self.request, {"MESSAGE_ID": "submission_patch"})
        )
