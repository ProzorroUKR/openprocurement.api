from logging import getLogger
from cornice.resource import resource
from pyramid.security import Allow, Everyone

from openprocurement.api.utils import (
    json_view,
    context_unpack,
    update_logging_context,
)
from openprocurement.api.views.base import MongodbResourceListing, RestrictedResourceListingMixin
from openprocurement.framework.core.procedure.context import get_object_config, get_object
from openprocurement.framework.core.procedure.serializers.submission import SubmissionSerializer
from openprocurement.framework.core.procedure.state.submission import SubmissionState
from openprocurement.framework.core.procedure.views.base import FrameworkBaseResource
from openprocurement.framework.core.procedure.utils import save_object
from openprocurement.framework.core.procedure.validation import validate_restricted_access
from openprocurement.tender.core.procedure.utils import set_ownership

LOGGER = getLogger(__name__)


SUBMISSION_OWNER_FIELDS = {"owner", "framework_owner"}


@resource(
    name="Submissions",
    path="/submissions",
    description="Submissions listing",
    request_method=("GET",),
)
class SubmissionsListResource(RestrictedResourceListingMixin, MongodbResourceListing):

    def __init__(self, request, context=None):
        super().__init__(request, context)
        self.listing_name = "Submissions"
        self.listing_default_fields = {"dateModified"}
        self.owner_fields = SUBMISSION_OWNER_FIELDS
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

    def __acl__(self):
        acl = [
            (Allow, Everyone, "view_listing"),
        ]
        return acl


class SubmissionsResource(FrameworkBaseResource):
    serializer_class = SubmissionSerializer
    state_class = SubmissionState

    def collection_post(self):
        update_logging_context(self.request, {"submission_id": "__new__"})
        submission = self.request.validated["data"]
        submission_config = get_object_config("submission")
        framework_config = get_object_config("framework")
        if framework_config.get("test", False):
            submission_config["test"] = framework_config["test"]
        if framework_config.get("restrictedDerivatives", False):
            submission_config["restricted"] = True
        self._serialize_config(self.request, "submission", submission_config)
        access = set_ownership(submission, self.request)
        self.state.on_post(submission)
        self.request.validated["submission"] = submission
        self.request.validated["submission_src"] = {}
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
                "config": get_object_config("submission"),
            }

    @json_view(
        validators=(
                validate_restricted_access("submission", owner_fields=SUBMISSION_OWNER_FIELDS)
        ),
        permission="view_framework",
    )
    def get(self):
        return {
            "data": self.serializer_class(get_object("submission")).data,
            "config": get_object_config("submission"),
        }

    def patch(self):
        updated = self.request.validated["data"]
        data = self.serializer_class(get_object("submission")).data
        if updated:
            before = self.request.validated["submission_src"]
            self.state.on_patch(before, updated)
            self.request.validated["submission"] = updated
            if save_object(self.request, "submission"):
                self.LOGGER.info(
                    f"Updated submission {updated['_id']}",
                    extra=context_unpack(self.request, {"MESSAGE_ID": "submission_patch"})
                )
            data = self.serializer_class(get_object("submission")).data
            self.state.after_patch(before, updated)
        return {
            "data": data,
            "config": get_object_config("submission"),
        }
