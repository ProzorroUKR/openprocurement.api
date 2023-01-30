from openprocurement.api.utils import (
    json_view,
    generate_id,
    set_ownership,
    context_unpack,
    upload_objects_documents,
)
from openprocurement.api.views.base import MongodbResourceListing
from openprocurement.framework.core.utils import (
    frameworksresource,
    generate_framework_pretty_id,
    save_framework,
)
from openprocurement.framework.core.validation import validate_framework_data


@frameworksresource(
    name="Frameworks",
    path="/frameworks",
    description="",
)
class FrameworkResource(MongodbResourceListing):
    def __init__(self, request, context):
        super(FrameworkResource, self).__init__(request, context)
        self.listing_name = "Frameworks"
        self.listing_default_fields = {"dateModified"}
        self.all_fields = {"dateCreated", "dateModified", "id", "title", "prettyID", "enquiryPeriod",
                           "period", "qualificationPeriod", "status", "frameworkType", "next_check"}
        self.db_listing_method = request.registry.mongodb.frameworks.list

    @json_view(
        content_type="application/json",
        permission="create_framework",
        validators=(
                validate_framework_data,
        )
    )
    def post(self):
        framework_id = generate_id()
        framework = self.request.validated["framework"]
        framework.id = framework_id
        if not framework.get("prettyID"):
            framework.prettyID = generate_framework_pretty_id(self.request)
        access = set_ownership(framework, self.request)
        upload_objects_documents(
            self.request, framework,
            route_kwargs={"framework_id": framework.id},
            route_prefix=framework["frameworkType"]
        )
        self.request.validated["framework"] = framework
        self.request.validated["framework_src"] = {}
        if save_framework(self.request, insert=True):
            self.LOGGER.info(
                "Created framework {} ({})".format(framework_id, framework.prettyID),
                extra=context_unpack(
                    self.request,
                    {"MESSAGE_ID": "framework_create"},
                    {"framework_id": framework_id, "prettyID": framework.prettyID,
                     "framework_mode": framework.mode},
                ),
            )
            self.request.response.status = 201
            self.request.response.headers["Location"] = self.request.route_url(
                "{}:Frameworks".format(framework.frameworkType), framework_id=framework_id
            )
            return {"data": framework.serialize(framework.status), "access": access}


@frameworksresource(
    name='FrameworkSubmissions',
    path='/frameworks/{frameworkID}/submissions',
    description="",
)
class FrameworkSubmissionRequestResource(MongodbResourceListing):
    filter_key = "frameworkID"

    def __init__(self, request, context):
        super().__init__(request, context)
        self.listing_name = "FrameworkSubmissions"
        self.listing_default_fields = {
            "dateModified", "dateCreated", "datePublished", "id", "date", "status",
            "qualificationID", "frameworkID", "tenderers",
        }
        self.listing_default_fields = {
            "dateModified", "dateCreated", "datePublished", "id", "date", "status",
            "qualificationID", "frameworkID", "tenderers",
        }
        self.db_listing_method = request.registry.mongodb.submissions.list


@frameworksresource(
    name='FrameworkQualifications',
    path='/frameworks/{frameworkID}/qualifications',
    description="",
)
class FrameworkQualificationRequestResource(MongodbResourceListing):
    filter_key = "frameworkID"

    def __init__(self, request, context):
        super().__init__(request, context)
        self.listing_name = "FrameworkQualifications"
        self.listing_default_fields = {
            "dateModified", "dateCreated", "id", "date", "status",
            "submissionID", "frameworkID", "documents",
        }
        self.all_fields = {
            "dateModified", "dateCreated", "id", "date", "status",
            "submissionID", "frameworkID", "documents",
        }
        self.db_listing_method = request.registry.mongodb.qualifications.list
