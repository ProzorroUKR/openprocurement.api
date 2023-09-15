from logging import getLogger
from cornice.resource import resource
from pyramid.security import Allow, Everyone

from openprocurement.api.utils import (
    json_view,
    context_unpack,
)
from openprocurement.api.views.base import MongodbResourceListing, RestrictedResourceListingMixin
from openprocurement.framework.core.procedure.state.qualification import QualificationState
from openprocurement.framework.core.procedure.validation import validate_restricted_access
from openprocurement.framework.core.procedure.context import get_object_config, get_object
from openprocurement.framework.core.procedure.serializers.qualification import QualificationSerializer
from openprocurement.framework.core.procedure.views.base import FrameworkBaseResource
from openprocurement.framework.core.procedure.utils import save_object

LOGGER = getLogger(__name__)
QUALIFICATION_OWNER_FIELDS = {"framework_owner", "submission_owner"}


@resource(
    name="Qualifications",
    path="/qualifications",
    description="Qualification listing",
    request_method=("GET",),
)
class QualificationsListResource(RestrictedResourceListingMixin, MongodbResourceListing):

    def __init__(self, request, context=None):
        super().__init__(request, context)
        self.listing_name = "Qualifications"
        self.owner_fields = QUALIFICATION_OWNER_FIELDS
        self.listing_default_fields = {"dateModified"}
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

    def __acl__(self):
        acl = [
            (Allow, Everyone, "view_listing"),
        ]
        return acl


class QualificationsResource(FrameworkBaseResource):
    serializer_class = QualificationSerializer
    state_class = QualificationState

    @json_view(
        validators=(
            validate_restricted_access("qualification", owner_fields=QUALIFICATION_OWNER_FIELDS)
        ),
        permission="view_framework",
    )
    def get(self):
        return {
            "data": self.serializer_class(get_object("qualification")).data,
            "config": get_object_config("qualification"),
        }

    def patch(self):
        updated = self.request.validated["data"]
        if updated:
            before = self.request.validated["qualification_src"]
            self.state.on_patch(before, updated)
            self.request.validated["qualification"] = updated
            if save_object(self.request, "qualification"):
                self.LOGGER.info(
                    f"Updated qualification {updated['_id']}",
                    extra=context_unpack(self.request, {"MESSAGE_ID": "qualification_patch"})
                )
            self.state.after_patch(before, updated)
        return {
            "data": self.serializer_class(get_object("qualification")).data,
            "config": get_object_config("qualification"),
        }
