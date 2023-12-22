from logging import getLogger
from cornice.resource import resource
from pyramid.security import Allow, Everyone, ALL_PERMISSIONS
from openprocurement.api.utils import (
    json_view,
    context_unpack,
    update_logging_context,
)
from openprocurement.api.views.base import MongodbResourceListing, BaseResource
from openprocurement.framework.core.procedure.context import get_object_config, get_object
from openprocurement.framework.core.procedure.serializers.framework import FrameworkSerializer
from openprocurement.framework.core.procedure.views.base import FrameworkBaseResource
from openprocurement.framework.core.procedure.utils import save_object
from openprocurement.framework.core.procedure.state.framework import FrameworkState
from openprocurement.framework.core.procedure.views.qualification import QualificationsListResource
from openprocurement.framework.core.procedure.views.submission import SubmissionsListResource
from openprocurement.tender.core.procedure.utils import set_ownership

LOGGER = getLogger(__name__)


@resource(
    name="Frameworks",
    path="/frameworks",
    description="Framework listing",
    request_method=("GET",),
)
class FrameworksListResource(MongodbResourceListing):

    def __init__(self, request, context=None):
        super().__init__(request, context)
        self.listing_name = "Frameworks"
        self.listing_default_fields = {"dateModified"}
        self.listing_allowed_fields = {
            "dateCreated",
            "dateModified",
            "id",
            "title",
            "prettyID",
            "enquiryPeriod",
            "period",
            "qualificationPeriod",
            "status",
            "frameworkType",
            "next_check",
        }
        self.db_listing_method = request.registry.mongodb.frameworks.list

    def __acl__(self):
        acl = [
            (Allow, Everyone, "view_listing"),
        ]
        return acl


class FrameworksResource(FrameworkBaseResource):
    serializer_class = FrameworkSerializer
    state_class = FrameworkState

    def collection_post(self):
        update_logging_context(self.request, {"framework_id": "__new__"})
        framework = self.request.validated["data"]
        framework_config = get_object_config("framework")
        self._serialize_config(self.request, "framework", framework_config)
        if framework_config.get("test"):
            framework["mode"] = "test"
        if framework.get("procuringEntity", {}).get("kind") == "defense":
            framework_config["restrictedDerivatives"] = True
        access = set_ownership(framework, self.request)
        self.state.on_post(framework)
        self.request.validated["framework"] = framework
        self.request.validated["framework_src"] = {}
        if save_object(self.request, "framework", insert=True):
            LOGGER.info(
                f"Created framework {framework['_id']} ({framework['prettyID']})",
                extra=context_unpack(
                    self.request,
                    {"MESSAGE_ID": "framework_create"},
                    {
                        "framework_id": framework["_id"],
                        "prettyID": framework["prettyID"],
                        "framework_mode": framework.get("mode"),
                    },
                ),
            )
            self.request.response.status = 201
            self.request.response.headers["Location"] = self.request.route_url(
                f"{framework['frameworkType']}:Frameworks", framework_id=framework["_id"]
            )
            return {
                "data": self.serializer_class(framework).data,
                "access": access,
                "config": get_object_config("framework"),
            }

    @json_view(permission="view_framework")
    def get(self):
        return {
            "data": self.serializer_class(get_object("framework")).data,
            "config": get_object_config("framework"),
        }

    def patch(self):
        updated = self.request.validated["data"]
        if self.request.authenticated_role == "chronograph":
            framework = self.request.validated["framework"]
            self.state.check_status(framework)
            self.state.update_next_check(framework)
            if save_object(self.request, "framework"):
                self.LOGGER.info(
                    "Updated framework by chronograph",
                    extra=context_unpack(self.request, {"MESSAGE_ID": "framework_chronograph_patch"})
                )
        elif updated:
            before = self.request.validated["framework_src"]
            self.request.validated["framework"] = updated
            self.state.on_patch(before, updated)
            if save_object(self.request, "framework"):
                self.LOGGER.info(
                    f"Updated framework {updated['_id']}",
                    extra=context_unpack(self.request, {"MESSAGE_ID": "framework_patch"})
                )
            self.state.after_patch(updated)
        return {
            "data": self.serializer_class(get_object("framework")).data,
            "config": get_object_config("framework"),
        }


@resource(
    name='FrameworkSubmissions',
    path='/frameworks/{frameworkID}/submissions',
    description="Framework Submissions",
)
class FrameworkSubmissionRequestResource(SubmissionsListResource):
    filter_key = "frameworkID"

    def __init__(self, request, context=None):
        super().__init__(request, context)
        self.listing_default_fields = {
            "dateModified",
            "dateCreated",
            "datePublished",
            "id",
            "date",
            "status",
            "qualificationID",
            "frameworkID",
            "tenderers",
        }


@resource(
    name='FrameworkQualifications',
    path='/frameworks/{frameworkID}/qualifications',
    description="Framework Qualifications",
)
class FrameworkQualificationRequestResource(QualificationsListResource):
    filter_key = "frameworkID"

    def __init__(self, request, context=None):
        super().__init__(request, context)
        self.listing_default_fields = {
            "dateModified",
            "dateCreated",
            "id",
            "frameworkID",
            "submissionID",
            "status",
            "documents",
            "date",
        }
