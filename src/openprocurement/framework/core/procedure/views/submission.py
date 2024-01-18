from logging import getLogger
from cornice.resource import resource
from pyramid.security import Allow, Everyone

from openprocurement.api.utils import (
    json_view,
    context_unpack,
    update_logging_context, request_fetch_submission, request_init_submission,
)
from openprocurement.api.views.base import MongodbResourceListing, RestrictedResourceListingMixin
from openprocurement.api.procedure.context import get_object, get_object_config, get_submission
from openprocurement.framework.core.procedure.mask import SUBMISSION_MASK_MAPPING
from openprocurement.framework.core.procedure.serializers.submission import SubmissionSerializer
from openprocurement.framework.core.procedure.state.framework import FrameworkState
from openprocurement.framework.core.procedure.views.base import FrameworkBaseResource
from openprocurement.framework.core.procedure.utils import save_object
from openprocurement.tender.core.procedure.utils import set_ownership

LOGGER = getLogger(__name__)


@resource(
    name="Submissions",
    path="/submissions",
    description="Submissions listing",
    request_method=("GET",),
)
class SubmissionsListResource(RestrictedResourceListingMixin, MongodbResourceListing):
    listing_name = "Submissions"
    listing_default_fields = {
        "dateModified",
    }
    listing_allowed_fields = {
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
    mask_mapping = SUBMISSION_MASK_MAPPING

    def __init__(self, request, context=None):
        super().__init__(request, context)
        self.db_listing_method = request.registry.mongodb.submissions.list

    def __acl__(self):
        acl = [
            (Allow, Everyone, "view_listing"),
        ]
        return acl


class SubmissionsResource(FrameworkBaseResource):
    serializer_class = SubmissionSerializer
    state_class = FrameworkState

    def collection_post(self):
        update_logging_context(self.request, {"submission_id": "__new__"})
        submission = self.request.validated["data"]
        request_init_submission(self.request, submission, submission_src={})
        access = set_ownership(submission, self.request)
        self.state.submission.on_post(submission)
        if save_object(self.request, "submission", insert=True):
            LOGGER.info(
                f"Created submission {submission['_id']}",
                extra=context_unpack(
                    self.request,
                    {"MESSAGE_ID": "submission_create"},
                    {
                        "submission_id": submission["_id"],
                        "submission_mode": submission.get("mode"),
                    },
                ),
            )
            self.request.response.status = 201
            self.request.response.headers["Location"] = self.request.route_url(
                f"{submission['submissionType']}:Submissions", submission_id=submission["_id"]
            )
            return {
                "data": self.serializer_class(submission).data,
                "access": access,
                "config": submission["config"],
            }

    @json_view(
        permission="view_framework",
    )
    def get(self):
        submission = get_submission()
        return {
            "data": self.serializer_class(submission).data,
            "config": submission["config"],
        }

    def patch(self):
        updated = self.request.validated["data"]
        submission = self.request.validated["submission"]
        submission_src = self.request.validated["submission_src"]
        if updated:
            self.state.submission.on_patch(submission_src, submission)
            self.save_all_objects()
        return {
            "data": self.serializer_class(submission).data,
            "config": submission["config"],
        }
