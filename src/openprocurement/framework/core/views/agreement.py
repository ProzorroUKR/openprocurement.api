from copy import deepcopy

from hashlib import sha512

from openprocurement.api.utils import (
    generate_id,
    json_view,
    set_ownership,
    get_now,
    upload_objects_documents,
    context_unpack,
    raise_operation_error,
)
from openprocurement.api.views.base import (
    MongodbResourceListing,
    BaseResource,
    RestrictedResourceListingMixin,
)
from openprocurement.framework.core.utils import (
    generate_agreement_id,
    save_agreement,
    agreementsresource,
    apply_patch,
    get_agreement_by_id,
    get_submission_by_id,
    check_agreement_status,
    check_contract_statuses,
)
from openprocurement.framework.core.validation import (
    validate_agreement_data,
    validate_restricted_access,
)


@agreementsresource(name="Agreements", path="/agreements")
class AgreementResource(RestrictedResourceListingMixin, MongodbResourceListing):
    def __init__(self, request, context):
        super().__init__(request, context)
        self.listing_name = "Agreements"
        self.listing_default_fields = {
            "dateModified",
        }
        self.listing_allowed_fields = {
            "dateCreated",
            "dateModified",
            "id",
            "agreementID",
            "agreementType",
            "status",
            "tender_id",
            "next_check",
        }
        self.listing_safe_fields = {
            "dateCreated",
            "dateModified",
            "id",
            "agreementID",
            "agreementType",
            "next_check",
        }
        self.db_listing_method = request.registry.mongodb.agreements.list

    @json_view(content_type="application/json", permission="create_agreement", validators=(validate_agreement_data,))
    def post(self):
        agreement = self.request.validated["agreement"]
        if not agreement.id:
            agreement_id = generate_id()
            agreement.id = agreement_id
        if not agreement.get("agreementID"):
            agreement.prettyID = generate_agreement_id(get_now(), self.db, self.server_id)

        # Unify when cfa moved from tenders to frameworks
        framework = self.request.validated.get("framework")
        if framework:
            agreement.submissionType = framework["frameworkType"]
            agreement.mode = framework.get("mode")
            upload_objects_documents(
                self.request, agreement,
                route_kwargs={"agreement_id": agreement.id},
                route_prefix=framework["frameworkType"]
            )

        access = set_ownership(agreement, self.request)
        self.request.validated["agreement"] = agreement
        self.request.validated["agreement_src"] = {}
        if save_agreement(self.request, insert=True):
            self.LOGGER.info(
                "Created agreement {} ({})".format(agreement.id, agreement.agreementID),
                extra=context_unpack(
                    self.request,
                    {"MESSAGE_ID": "agreement_create"},
                    {"agreement_id": agreement.id, "agreementID": agreement.agreementID},
                ),
            )
            self.request.response.status = 201
            self.request.response.headers["Location"] = self.request.route_url(
                "{}:Agreements".format(agreement.agreementType), agreement_id=agreement.id
            )
            return {"data": agreement.serialize("view"), "access": access}


class CoreAgreementResource(BaseResource):
    @json_view(
        validators=(
            validate_restricted_access("agreement")
        ),
        permission="view_agreement",
    )
    def get(self):
        agreement_config = self.request.validated["agreement_config"]

        response_data = {"data": self.context.serialize("view")}
        if agreement_config:
            response_data["config"] = agreement_config

        return response_data

    def patch(self):
        agreement_config = self.request.validated["agreement_config"]
        if self.request.authenticated_role == "chronograph":
            now = get_now()
            if not check_agreement_status(self.request, now):
                check_contract_statuses(self.request, now)
        if apply_patch(
            self.request,
            obj_name="agreement",
            data=self.request.validated["agreement"].to_primitive(),
            src=self.request.validated["agreement_src"]
        ):
            self.LOGGER.info(
                f"Updated agreement {self.request.validated['agreement'].id}",
                extra=context_unpack(self.request, {"MESSAGE_ID": "agreement_patch"}),
            )

        response_data = {"data": self.request.context.serialize("view")}
        if agreement_config:
            response_data["config"] = agreement_config

        return response_data


@agreementsresource(
    name="Agreements by classificationID",
    path="/agreements_by_classification/{classification_id}",
    description="Agreements filter classification"
)
class AgreementFilterByClassificationResource(BaseResource):
    @json_view(permission="view_listing")
    def get(self):

        classification_id = self.request.matchdict.get("classification_id")
        if "-" in classification_id:
            classification_id = classification_id[:classification_id.find("-")]
        additional_classifications = self.request.params.get("additional_classifications", "")

        if additional_classifications.lower() == "none":
            additional_classifications = set()
        elif additional_classifications:
            additional_classifications = set(additional_classifications.split(","))

        results = self.request.registry.mongodb.agreements.list_by_classification_id(classification_id)
        if isinstance(additional_classifications, set):
            results = [
                x for x in results
                if {i['id'] for i in x.get("additionalClassifications", "")} == additional_classifications
            ]

        return {"data": results}


class AgreementViewMixin:
    request = None
    LOGGER = None
    server_id = None

    def get_or_create_agreement(self):
        framework_config = self.request.validated["framework_config"]
        framework_data = self.request.validated["framework_src"]
        agreementID = framework_data.get("agreementID")
        if agreementID:
            agreement = get_agreement_by_id(self.request, agreementID)
            if not agreement:
                raise_operation_error(
                    self.request,
                    "agreementID must be one of exists agreement",
                )
            model = self.request.agreement_from_data(agreement, create=False)
            self.request.validated["agreement"] = agreement = model(agreement)
            agreement.__parent__ = self.request.validated["qualification"].__parent__
            self.request.validated["agreement_src"] = agreement.serialize("plain")
        else:
            agreement_id = generate_id()
            now = get_now()
            transfer = generate_id()
            transfer_token = sha512(transfer.encode("utf-8")).hexdigest()
            agreement_data = {
                "id": agreement_id,
                "agreementID": generate_agreement_id(self.request),
                "frameworkID": framework_data["id"],
                "agreementType": framework_data["frameworkType"],
                "status": "active",
                "period": {
                    "startDate": now,
                    "endDate": framework_data.get("qualificationPeriod").get("endDate")
                },
                "procuringEntity": framework_data.get("procuringEntity"),
                "classification": framework_data.get("classification"),
                "additionalClassifications": framework_data.get("additionalClassifications"),
                "contracts": [],
                "owner": framework_data["owner"],
                "owner_token": framework_data["owner_token"],
                "mode": framework_data.get("mode"),
                "dateModified": now,
                "date": now,
                "transfer_token": transfer_token,
                "frameworkDetails": framework_data.get("frameworkDetails"),
            }
            agreement_config = {}
            if framework_config.get("test", False):
                agreement_config["test"] = framework_config["test"]
            if framework_config.get("restrictedDerivatives", False):
                agreement_config["restricted"] = True
            model = self.request.agreement_from_data(agreement_data, create=False)
            agreement = model(agreement_data)

            self.request.validated["agreement_src"] = {}
            self.request.validated["agreement"] = agreement
            self.request.validated["agreement_config"] = agreement_config
            if save_agreement(self.request, insert=True):
                self.LOGGER.info(
                    "Created agreement {}".format(agreement_id),
                    extra=context_unpack(
                        self.request,
                        {"MESSAGE_ID": "agreement_create"},
                        {
                            "agreement_id": agreement_id,
                            "agreement_mode": agreement.mode
                        },
                    ),
                )

                framework_data_updated = {"agreementID": agreement_id}
                apply_patch(
                    self.request, data=framework_data_updated, src=self.request.validated["framework_src"],
                    obj_name="framework"
                )
                self.LOGGER.info(
                    "Updated framework {} with agreementID".format(framework_data["id"]),
                    extra=context_unpack(self.request, {"MESSAGE_ID": "qualification_patch"}),
                )

    def create_agreement_contract(self):
        qualification = self.request.validated["qualification"]
        framework = self.request.validated["framework"]
        agreement_data = get_agreement_by_id(self.request, framework.agreementID)
        if not agreement_data:
            raise_operation_error(
                self.request,
                "agreementID must be one of exists agreement",
            )
        submission_data = get_submission_by_id(self.request, qualification.submissionID)
        if not agreement_data:
            raise_operation_error(
                self.request,
                "submissionID must be one of exists submission",
            )
        if agreement_data["status"] != "active":
            return

        contract_id = generate_id()
        first_milestone_data = {
            "type": "activation",
            "dueDate": framework.get("qualificationPeriod").get("endDate")
        }
        contract_data = {
            "id": contract_id,
            "qualificationID": qualification.id,
            "submissionID": submission_data["_id"],
            "status": "active",
            "suppliers": submission_data["tenderers"],
            "milestones": [first_milestone_data],
        }
        new_contracts = deepcopy(agreement_data.get("contracts", []))
        new_contracts.append(contract_data)

        apply_patch(self.request, data={"contracts": new_contracts}, src=agreement_data, obj_name="agreement")
        self.LOGGER.info(
            "Updated agreement {} with contract {}".format(agreement_data["_id"], contract_id),
            extra=context_unpack(self.request, {"MESSAGE_ID": "qualification_patch"}),
        )
