from openprocurement.api.utils import (
    json_view,
    generate_id,
    set_ownership,
    context_unpack,
    upload_objects_documents,
    raise_operation_error,
)
from openprocurement.api.views.base import (
    MongodbResourceListing,
    BaseResource,
)
from openprocurement.framework.core.utils import (
    frameworksresource,
    generate_framework_pretty_id,
    save_framework,
    apply_patch,
    calculate_framework_periods,
    check_status,
)
from openprocurement.framework.core.validation import (
    validate_framework_data,
    validate_qualification_period_duration,
)

AGREEMENT_DEPENDENT_FIELDS = ("qualificationPeriod", "procuringEntity")

MIN_QUALIFICATION_DURATION = 30
MAX_QUALIFICATION_DURATION = 1095


@frameworksresource(
    name="Frameworks",
    path="/frameworks",
    description="Frameworks",
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
                    {
                        "framework_id": framework_id, "prettyID": framework.prettyID,
                        "framework_mode": framework.mode,
                    },
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
    description="Framework Submissions",
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
    description="Framework Qualifications",
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


class CoreFrameworkResource(BaseResource):
    @json_view(permission="view_framework")
    def get(self):
        if self.request.authenticated_role == "chronograph":
            framework_data = self.context.serialize("chronograph_view")
        else:
            framework_data = self.context.serialize(self.context.status)
        return {"data": framework_data}

    def patch(self):
        framework = self.context
        if self.request.authenticated_role == "chronograph":
            check_status(self.request)
            save_framework(self.request)
        else:
            if self.request.validated["data"].get("status") not in ("draft", "active"):
                raise_operation_error(
                    self.request,
                    "Can't switch to {} status".format(self.request.validated["data"].get("status")),
                )
            if self.request.validated["data"].get("status") == "active":
                model = self.request.context._fields["qualificationPeriod"]
                calculate_framework_periods(self.request, model)
                validate_qualification_period_duration(
                    self.request,
                    model,
                    MIN_QUALIFICATION_DURATION,
                    MAX_QUALIFICATION_DURATION,
                )

            apply_patch(
                self.request,
                src=self.request.validated["framework_src"],
                obj_name="framework",
            )

            if (
                any([f in self.request.validated["json_data"] for f in AGREEMENT_DEPENDENT_FIELDS])
                and framework.agreementID
                and self.request.validated["agreement_src"]["status"] == "active"
            ):
                self.update_agreement()

        self.LOGGER.info(
            "Updated framework {}".format(framework.id),
            extra=context_unpack(self.request, {"MESSAGE_ID": "framework_patch"}),
        )
        # TODO: Change to chronograph_view for chronograph
        return {"data": framework.serialize(framework.status)}

    def update_agreement(self):
        framework = self.request.validated["framework"]

        updated_agreement_data = {
            "period": {
                "startDate": self.request.validated["agreement_src"]["period"]["startDate"],
                "endDate": framework.qualificationPeriod.endDate.isoformat()
            },
            "procuringEntity": framework.procuringEntity
        }
        apply_patch(
            self.request,
            src=self.request.validated["agreement_src"],
            data=updated_agreement_data,
            obj_name="agreement",
        )
        self.LOGGER.info(
            "Updated agreement {}".format(self.request.validated["agreement_src"]["id"]),
            extra=context_unpack(self.request, {"MESSAGE_ID": "framework_patch"}),
        )
