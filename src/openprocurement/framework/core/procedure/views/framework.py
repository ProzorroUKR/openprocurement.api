from logging import getLogger
from cornice.resource import resource
from pyramid.security import Allow, Everyone
from openprocurement.api.utils import (
    json_view,
    context_unpack,
    update_logging_context,
    request_init_framework,
    request_fetch_agreement,
)
from openprocurement.api.views.base import MongodbResourceListing
from openprocurement.api.procedure.context import get_framework
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
    listing_name = "Frameworks"
    listing_default_fields = {
        "dateModified",
    }
    listing_allowed_fields = {
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

    def __init__(self, request, context=None):
        super().__init__(request, context)
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
        request_init_framework(self.request, framework, framework_src={})
        access = set_ownership(framework, self.request)
        self.state.on_post(framework)
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
                "config": framework["config"],
            }

    @json_view(permission="view_framework")
    def get(self):
        framework = get_framework()
        return {
            "data": self.serializer_class(framework).data,
            "config": framework["config"],
        }

    def patch(self):
        updated = self.request.validated["data"]
        framework = self.request.validated["framework"]
        framework_src = self.request.validated["framework_src"]
        if self.request.authenticated_role == "chronograph":
            self.state.check_status(framework)
            self.state.update_next_check(framework)
            if save_object(self.request, "framework"):
                self.LOGGER.info(
                    "Updated framework by chronograph",
                    extra=context_unpack(self.request, {"MESSAGE_ID": "framework_chronograph_patch"}),
                )
        elif updated:
            framework = self.request.validated["framework"] = updated
            self.state.on_patch(framework_src, framework)
            if save_object(self.request, "framework"):
                self.LOGGER.info(
                    f"Updated framework {framework['_id']}",
                    extra=context_unpack(self.request, {"MESSAGE_ID": "framework_patch"}),
                )
            self.state.after_patch(updated)
        return {
            "data": self.serializer_class(framework).data,
            "config": framework["config"],
        }


@resource(
    name='FrameworkSubmissions',
    path='/frameworks/{frameworkID}/submissions',
    description="Framework Submissions",
)
class FrameworkSubmissionRequestResource(SubmissionsListResource):
    filter_key = "frameworkID"
    listing_default_fields = {
        "dateModified",
        "dateCreated",
        "datePublished",
        "id",
        "date",
        "status",
        "qualificationID",
        "frameworkID",
        "documents",
        "tenderers",
    }


@resource(
    name='FrameworkQualifications',
    path='/frameworks/{frameworkID}/qualifications',
    description="Framework Qualifications",
)
class FrameworkQualificationRequestResource(QualificationsListResource):
    filter_key = "frameworkID"
    listing_default_fields = {
        "dateModified",
        "dateCreated",
        "id",
        "frameworkID",
        "submissionID",
        "status",
        "documents",
        "date",
    }
