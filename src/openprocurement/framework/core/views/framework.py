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
from openprocurement.framework.core.models import FrameworkConfig
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
from openprocurement.framework.core.views.qualification import QualificationResource
from openprocurement.framework.core.views.submission import SubmissionResource
from openprocurement.tender.core.procedure.validation import validate_config_data

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
        self.listing_default_fields = {
            "dateModified",
        }
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

    @json_view(
        content_type="application/json",
        permission="create_framework",
        validators=(
            validate_framework_data,
            validate_config_data(FrameworkConfig, obj_name="framework"),
        )
    )
    def post(self):
        framework_config = self.request.validated["framework_config"]
        framework_id = generate_id()
        framework = self.request.validated["framework"]
        framework.id = framework_id
        if framework_config.get("test"):
            framework.mode = "test"
        if not framework.get("prettyID"):
            framework.prettyID = generate_framework_pretty_id(self.request)
        if framework["procuringEntity"]["kind"] == "defense":
            framework_config["restrictedDerivatives"] = True
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
            response_data = {"data": framework.serialize(framework.status), "access": access}
            if framework_config:
                response_data["config"] = framework_config
            return response_data


@frameworksresource(
    name='FrameworkSubmissions',
    path='/frameworks/{frameworkID}/submissions',
    description="Framework Submissions",
)
class FrameworkSubmissionRequestResource(SubmissionResource):
    filter_key = "frameworkID"

    def __init__(self, request, context):
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


@frameworksresource(
    name='FrameworkQualifications',
    path='/frameworks/{frameworkID}/qualifications',
    description="Framework Qualifications",
)
class FrameworkQualificationRequestResource(QualificationResource):
    filter_key = "frameworkID"

    def __init__(self, request, context):
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


class CoreFrameworkResource(BaseResource):
    @json_view(permission="view_framework")
    def get(self):
        config = self.request.validated["framework_config"]
        if self.request.authenticated_role == "chronograph":
            framework_data = self.context.serialize("chronograph_view")
        else:
            framework_data = self.context.serialize(self.context.status)
        response_data = {"data": framework_data}
        if config:
            response_data["config"] = config
        return response_data

    def patch(self):
        framework_config = self.request.validated["framework_config"]
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
        response_data = {"data": framework.serialize(framework.status)}
        if framework_config:
            response_data["config"] = framework_config
        return response_data

    def update_agreement(self):
        framework = self.request.validated["framework"]
        agreement_data = self.request.validated["agreement_src"]

        end_date = framework.qualificationPeriod.endDate.isoformat()

        updated_agreement_data = {
            "period": {
                "startDate": agreement_data["period"]["startDate"],
                "endDate": end_date,
            },
            "procuringEntity": framework.procuringEntity,
            "contracts": agreement_data["contracts"],
        }
        for contract in updated_agreement_data["contracts"]:
            for milestone in contract["milestones"]:
                if milestone["type"] == "activation":
                    milestone["dueDate"] = end_date

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
