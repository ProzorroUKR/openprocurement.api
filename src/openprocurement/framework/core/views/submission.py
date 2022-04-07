import simplejson
from pyramid.request import Request

from openprocurement.api.constants import VERSION, FAST_CATALOGUE_FLOW
from openprocurement.api.utils import (
    APIResourceListing,
    json_view,
    generate_id,
    set_ownership,
    context_unpack,
    upload_objects_documents,
)
from openprocurement.framework.core.design import (
    SUBMISSION_FIELDS,
    submissions_by_dateModified_view,
    submissions_test_by_dateModified_view,
    submissions_by_local_seq_view,
    submissions_test_by_local_seq_view,
)
from openprocurement.framework.core.utils import submissionsresource, save_submission
from openprocurement.framework.core.validation import (
    validate_submission_data,
    validate_operation_submission_in_not_allowed_period,
    validate_action_in_not_allowed_framework_status,
    validate_post_submission_with_active_contract,
)

VIEW_MAP = {
    "": submissions_by_dateModified_view,
    "test": submissions_test_by_dateModified_view,
    "_all_": submissions_by_dateModified_view,

}
CHANGES_VIEW_MAP = {
    "": submissions_by_local_seq_view,
    "test": submissions_test_by_local_seq_view,
    "_all_": submissions_by_local_seq_view,
}
FEED = {"dateModified": VIEW_MAP, "changes": CHANGES_VIEW_MAP}


@submissionsresource(
    name="Submissions",
    path="/submissions",
    description="Create Submission",
)
class SubmissionResource(APIResourceListing):
    def __init__(self, request, context):
        super(SubmissionResource, self).__init__(request, context)
        # params for listing
        self.VIEW_MAP = VIEW_MAP
        self.CHANGES_VIEW_MAP = CHANGES_VIEW_MAP
        self.FEED = FEED
        self.FIELDS = SUBMISSION_FIELDS
        self.object_name_for_listing = "Submissions"
        self.log_message_id = "submission_list_custom"
        self.db = request.registry.databases.submissions

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
        if save_submission(self.request):
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

            if FAST_CATALOGUE_FLOW:
                # TODO: Remove this branch after the war ends
                #  Russian warship, go fuck yourself

                headers = self.request.headers
                headers["Content-type"] = "application/json; charset=utf-8"

                # activate submission
                submission_token = access["token"]
                sub_req = Request.blank(
                    f'/api/{VERSION}/submissions/{submission_id}?acc_token={submission_token}',
                    environ={"REQUEST_METHOD": "PATCH"},
                    headers=headers,
                )
                sub_req.body = simplejson.dumps({"data": {"status": "active"}}).encode()
                response = self.request.invoke_subrequest(sub_req, use_tweens=True)
                if "errors" in response.json:
                    self.request.response.status = response.status
                    return response.json

                # activate qualification
                qualification_id = response.json["data"]["qualificationID"]
                framework_token = framework["owner_token"]
                sub_req = Request.blank(
                    f'/api/{VERSION}/qualifications/{qualification_id}?acc_token={framework_token}',
                    environ={"REQUEST_METHOD": "PATCH"},
                    headers=headers,
                )
                sub_req.body = simplejson.dumps({"data": {"status": "active"}}).encode()
                response = self.request.invoke_subrequest(sub_req, use_tweens=True)
                if "errors" in response.json:
                    self.request.response.status = response.status
                    return response.json

                # get submission
                sub_req = Request.blank(
                    f'/api/{VERSION}/submissions/{submission_id}',
                    environ={"REQUEST_METHOD": "GET"},
                    headers=headers,
                )
                sub_req.body = b""
                response = self.request.invoke_subrequest(sub_req, use_tweens=True)
                if "errors" in response.json:
                    self.request.response.status = response.status
                    return response.json

                return {"data": response.json["data"], "access": access}

            return {"data": submission.serialize("view"), "access": access}

