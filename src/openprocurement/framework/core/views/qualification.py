from openprocurement.api.views.base import (
    MongodbResourceListing,
    RestrictedResourceListingMixin,
)
from openprocurement.api.utils import (
    json_view,
    context_unpack,
    get_now,
)
from openprocurement.api.views.base import BaseResource
from openprocurement.framework.core.utils import (
    qualificationsresource,
    apply_patch,
    get_submission_by_id,
)
from openprocurement.framework.core.validation import validate_restricted_access
from openprocurement.framework.core.views.agreement import AgreementViewMixin


QUALIFICATION_OWNER_FIELDS = {"framework_owner", "submission_owner"}


@qualificationsresource(
    name="Qualifications",
    path="/qualifications",
    description="",  # TODO: Add description
)
class QualificationResource(RestrictedResourceListingMixin, MongodbResourceListing):
    def __init__(self, request, context):
        super().__init__(request, context)
        self.listing_name = "Qualifications"
        self.owner_fields = QUALIFICATION_OWNER_FIELDS
        self.listing_default_fields = {
            "dateModified",
        }
        self.listing_allowed_fields = {
            "dateModified",
            "dateCreated",
            "id",
            "frameworkID",
            "submissionID",
            "qualificationType",
            "status",
            "documents",
            "date",
        }
        self.listing_safe_fields = {
            "dateModified",
            "dateCreated",
            "id",
            "frameworkID",
            "submissionID",
            "qualificationType",
        }
        self.db_listing_method = request.registry.mongodb.qualifications.list


class CoreQualificationResource(BaseResource, AgreementViewMixin):
    @json_view(
        validators=(
            validate_restricted_access("qualification", owner_fields=QUALIFICATION_OWNER_FIELDS)
        ),
        permission="view_qualification",
    )
    def get(self):
        """
        Get info by qualification
        """
        qualification_config = self.request.validated["qualification_config"]
        qualification_data = self.context.serialize("view")

        response_data = {"data": qualification_data}
        if qualification_config:
            response_data["config"] = qualification_config

        return response_data

    def patch(self):
        """
        Qualification edit(partial)
        """
        qualification_config = self.request.validated["qualification_config"]
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
            self.get_or_create_agreement()
            self.create_agreement_contract()

        response_data = {"data": qualification.serialize("view")}
        if qualification_config:
            response_data["config"] = qualification_config

        return response_data

    def complete_submission(self):
        qualification = self.request.validated["qualification"]
        submission_data = get_submission_by_id(self.request, qualification.submissionID)
        model = self.request.submission_from_data(submission_data, create=False)
        submission = model(submission_data)
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
