from openprocurement.api.utils import (
    set_ownership,
    upload_objects_documents,
)
from openprocurement.api.views.base import (
    MongodbResourceListing,
    RestrictedResourceListingMixin,
)
from openprocurement.api.constants import FAST_CATALOGUE_FLOW_FRAMEWORK_IDS
from openprocurement.api.utils import (
    json_view,
    context_unpack,
    get_now,
    generate_id,
)
from openprocurement.api.views.base import BaseResource
from openprocurement.framework.core.models import SubmissionConfig
from openprocurement.framework.core.utils import (
    submissionsresource,
    apply_patch,
    save_submission,
    save_qualification,
)
from openprocurement.framework.core.validation import (
    validate_submission_data,
    validate_post_submission_with_active_contract,
    validate_operation_submission_in_not_allowed_period,
    validate_action_in_not_allowed_framework_status,
    validate_restricted_access,
)
from openprocurement.framework.core.views.agreement import AgreementViewMixin
from openprocurement.tender.core.procedure.validation import validate_config_data


SUBMISSION_OWNER_FIELDS = {"owner", "framework_owner"}


@submissionsresource(
    name="Submissions",
    path="/submissions",
    description="Create Submission",
)
class SubmissionResource(RestrictedResourceListingMixin, MongodbResourceListing):
    def __init__(self, request, context):
        super().__init__(request, context)
        self.listing_name = "Submissions"
        self.owner_fields = SUBMISSION_OWNER_FIELDS
        self.listing_default_fields = {
            "dateModified",
        }
        self.listing_allowed_fields = {
            "dateCreated",
            "dateModified",
            "id",
            "frameworkID",
            "qualificationID",
            "submissionType",
            "status",
            "tenderers",
            "documents",
            "date",
            "datePublished",
        }
        self.listing_safe_fields = {
            "dateCreated",
            "dateModified",
            "id",
            "frameworkID",
            "qualificationID",
            "submissionType",
        }
        self.db_listing_method = request.registry.mongodb.submissions.list

    @json_view(
        content_type="application/json",
        permission="create_submission",
        validators=(
            validate_submission_data,
            validate_config_data(SubmissionConfig, obj_name="submission"),
            validate_operation_submission_in_not_allowed_period,
            validate_action_in_not_allowed_framework_status("submission"),
            validate_post_submission_with_active_contract,
        )
    )
    def post(self):
        """
        Creating new submission
        """
        submission_config = self.request.validated["submission_config"]
        submission_id = generate_id()
        submission = self.request.validated["submission"]
        submission.id = submission_id
        framework_config = self.request.validated["framework_config"]
        framework = self.request.validated["framework"]
        self.LOGGER.info(framework["frameworkType"])
        submission.submissionType = framework["frameworkType"]
        submission.mode = framework.get("mode")
        submission.framework_owner = framework["owner"]
        submission.framework_token = framework["owner_token"]
        if framework_config.get("test", False):
            submission_config["test"] = framework_config["test"]
        if framework_config.get("restrictedDerivatives", False):
            submission_config["restricted"] = True
        if self.request.json["data"].get("status") == "draft":
            submission.status = "draft"
        upload_objects_documents(
            self.request, submission,
            route_kwargs={"submission_id": submission.id},
            route_prefix=framework["frameworkType"]
        )
        access = set_ownership(submission, self.request)
        self.request.validated["submission"] = submission
        self.request.validated["submission_src"] = {}
        if save_submission(self.request, insert=True):
            self.LOGGER.info(
                "Created submission {}".format(submission_id),
                extra=context_unpack(
                    self.request,
                    {"MESSAGE_ID": "submission_create"},
                    {
                        "submission_id": submission_id,
                        "submission_mode": submission.mode
                    },
                ),
            )
            self.request.response.status = 201
            self.request.response.headers["Location"] = self.request.route_url(
                "{}:Submissions".format(submission.submissionType), submission_id=submission_id
            )
            response_data = {"data": submission.serialize("view"), "access": access}
            if submission_config:
                response_data["config"] = submission_config
            return response_data


class CoreSubmissionResource(BaseResource, AgreementViewMixin):
    @json_view(
        validators=(
            validate_restricted_access("submission", owner_fields=SUBMISSION_OWNER_FIELDS)
        ),
        permission="view_submission",
    )
    def get(self):
        """
        Get info by submission
        """
        submission_config = self.request.validated["submission_config"]
        submission_data = self.context.serialize("view")
        response_data = {"data": submission_data}
        if submission_config:
            response_data["config"] = submission_config
        return response_data

    def patch(self):
        """
        Submission edit(partial)
        """
        submission_config = self.request.validated["submission_config"]
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
            self.get_or_create_agreement()
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

        response_data = {"data": data}
        if submission_config:
            response_data["config"] = submission_config

        return response_data

    def create_qualification(self):
        submission = self.request.context
        framework = self.request.validated["framework"]
        framework_config = self.request.validated["framework_config"]

        qualification_id = generate_id()
        qualification_data = {
            "id": qualification_id,
            "frameworkID": framework["_id"],
            "submissionID": submission.id,
            "framework_owner": framework["owner"],
            "framework_token": framework["owner_token"],
            "submission_owner": submission["owner"],
            "submission_token": submission["owner_token"],
            "qualificationType": framework["frameworkType"],
            "mode": framework.get("mode")
        }
        qualification_config = {}
        if framework_config.get("test", False):
            qualification_config["test"] = framework_config["test"]
        if framework_config.get("restrictedDerivatives", False):
            qualification_config["restricted"] = True
        model = self.request.qualification_from_data(qualification_data, create=False)
        qualification = model(qualification_data)
        self.request.validated["qualification_src"] = {}
        self.request.validated["qualification"] = qualification
        self.request.validated["qualification_config"] = qualification_config

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
