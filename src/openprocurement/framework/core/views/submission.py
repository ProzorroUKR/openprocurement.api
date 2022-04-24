from openprocurement.api.utils import (
    MongodbResourceListing,
    json_view,
    generate_id,
    set_ownership,
    context_unpack,
    upload_objects_documents,
)
from openprocurement.framework.core.utils import submissionsresource, save_submission
from openprocurement.framework.core.validation import (
    validate_submission_data,
    validate_operation_submission_in_not_allowed_period,
    validate_action_in_not_allowed_framework_status,
    validate_post_submission_with_active_contract,
)


@submissionsresource(
    name="Submissions",
    path="/submissions",
    description="Create Submission",
)
class SubmissionResource(MongodbResourceListing):
    def __init__(self, request, context):
        super().__init__(request, context)
        self.listing_name = "Submissions"
        self.listing_default_fields = {"dateModified"}
        self.all_fields = {"dateCreated", "dateModified", "id", "frameworkID", "qualificationID", "status",
                           "tenderers", "documents", "date", "datePublished"}
        self.db_listing_method = request.registry.mongodb.submissions.list

    @json_view(
        content_type="application/json",
        permission="create_submission",
        validators=(
            validate_submission_data,
            validate_operation_submission_in_not_allowed_period,
            validate_action_in_not_allowed_framework_status("submission"),
            validate_post_submission_with_active_contract,
        )
    )
    def post(self):
        """
        Creating new submission
        """
        submission_id = generate_id()
        submission = self.request.validated["submission"]
        submission.id = submission_id
        framework = self.request.validated["framework"]
        submission.submissionType = framework["frameworkType"]
        submission.mode = framework.get("mode")
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
                    {"submission_id": submission_id,
                     "submission_mode": submission.mode},
                ),
            )
            self.request.response.status = 201
            self.request.response.headers["Location"] = self.request.route_url(
                "{}:Submissions".format(submission.submissionType), submission_id=submission_id
            )
            return {"data": submission.serialize("view"), "access": access}

