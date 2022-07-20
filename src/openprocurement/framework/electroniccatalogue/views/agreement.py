from copy import deepcopy

from hashlib import sha512

from openprocurement.api.utils import (
    json_view, context_unpack, get_now, raise_operation_error,
    generate_id,
)
from openprocurement.api.views.base import BaseResource
from openprocurement.framework.core.utils import (
    agreementsresource, apply_patch, get_agreement_by_id,
    generate_agreementID, save_agreement, get_submission_by_id,
)
from openprocurement.framework.core.validation import validate_patch_agreement_data
from openprocurement.framework.electroniccatalogue.models import Agreement
from openprocurement.framework.electroniccatalogue.utils import check_contract_statuses, check_agreement_status
from openprocurement.framework.electroniccatalogue.validation import validate_agreement_operation_not_in_allowed_status


@agreementsresource(
    name="electronicCatalogue:Agreements",
    path="/agreements/{agreement_id}",
    agreementType="electronicCatalogue",
    description="Agreements resource"
)
class AgreementResource(BaseResource):
    @json_view(permission="view_agreement")
    def get(self):
        return {"data": self.context.serialize("view")}

    @json_view(
        content_type="application/json",
        validators=(
                validate_patch_agreement_data,
                validate_agreement_operation_not_in_allowed_status,
        ),
        permission="edit_agreement"
    )
    def patch(self):
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
            self.LOGGER.info(f"Updated agreement {self.request.validated['agreement'].id}",
                             extra=context_unpack(self.request, {"MESSAGE_ID": "agreement_patch"}))
        return {"data": self.request.context.serialize("view")}


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

        data = {
            "data": results,
        }
        return data


class AgreementMixin:
    request = None
    LOGGER = None
    server_id = None


    def ensure_agreement(self):
        framework_data = self.request.validated["framework_src"]
        agreementID = framework_data.get("agreementID")
        if agreementID:
            agreement = get_agreement_by_id(self.request, agreementID)
            if not agreement:
                raise_operation_error(
                    self.request,
                    "agreementID must be one of exists agreement",
                )
            self.request.validated["agreement"] = agreement = Agreement(agreement)
            agreement.__parent__ = self.request.validated["qualification"].__parent__
            self.request.validated["agreement_src"] = agreement.serialize("plain")
        else:
            agreement_id = generate_id()
            now = get_now()
            transfer = generate_id()
            transfer_token = sha512(transfer.encode("utf-8")).hexdigest()
            agreement_data = {
                "id": agreement_id,
                "agreementID": generate_agreementID(self.request),
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
            agreement = Agreement(agreement_data)

            self.request.validated["agreement_src"] = {}
            self.request.validated["agreement"] = agreement
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
                    extra=context_unpack(self.request, {"MESSAGE_ID": "qualification_patch"})
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
            extra=context_unpack(self.request, {"MESSAGE_ID": "qualification_patch"})
        )
