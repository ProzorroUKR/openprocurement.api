from copy import deepcopy
from logging import getLogger
from hashlib import sha512

from openprocurement.api.context import get_request, get_now
from openprocurement.api.utils import raise_operation_error, generate_id, context_unpack
from openprocurement.framework.core.procedure.models.agreement import (
    PostAgreement,
    PatchAgreement,
    AgreementChronographData,
)
from openprocurement.framework.core.procedure.state.chronograph import ChronographEventsMixing
from openprocurement.framework.core.procedure.utils import save_object
from openprocurement.framework.core.utils import get_agreement_by_id, get_submission_by_id
from openprocurement.tender.core.procedure.state.base import BaseState

LOGGER = getLogger(__name__)


class AgreementState(ChronographEventsMixing, BaseState):

    def on_post(self, data):
        self.set_agreement_data(data)
        super().on_post(data)

    def always(self, data):
        agreement = get_request().validated["agreement"]
        self.update_next_check(agreement)

    def set_agreement_data(self, agreement):
        # Unify when cfa moved from tenders to frameworks
        framework = get_request().validated.get("framework")
        if framework:
            agreement["agreementType"] = framework["frameworkType"]
            agreement["mode"] = framework.get("mode")

    def get_patch_data_model(self):
        request = get_request()
        if request.authenticated_role == "chronograph":
            return AgreementChronographData
        return PatchAgreement

    def get_next_check(self, data):
        checks = []
        if data["status"] == "active":
            milestone_dueDates = [
                milestone["dueDate"]
                for contract in data.get("contracts", []) for milestone in contract.get("milestones", [])
                if milestone["dueDate"] and milestone["status"] == "scheduled"
            ]
            if milestone_dueDates:
                checks.append(min(milestone_dueDates))
            checks.append(data["period"]["endDate"])
        return min(checks) if checks else None


class AgreementStateMixin:
    agreement_model = PostAgreement

    def get_or_create_agreement(self):
        framework_config = get_request().validated["framework_config"]
        framework_data = get_request().validated["framework_src"]
        agreementID = framework_data.get("agreementID")
        if agreementID:
            agreement = get_agreement_by_id(get_request(), agreementID)
            if not agreement:
                raise_operation_error(
                    get_request(),
                    "agreementID must be one of exists agreement",
                )
            model = get_request().agreement_from_data(agreement, create=False)
            agreement = model(agreement)
            get_request().validated["agreement"] = agreement.serialize()
            get_request().validated["agreement_src"] = deepcopy(get_request().validated["agreement"])
        else:
            now = get_now().isoformat()
            transfer = generate_id()
            transfer_token = sha512(transfer.encode("utf-8")).hexdigest()
            agreement_data = {
                "frameworkID": framework_data["_id"],
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
            agreement = self.agreement_model(agreement_data).serialize()

            get_request().validated["agreement_src"] = {}
            get_request().validated["agreement"] = agreement
            get_request().validated["agreement_config"] = agreement_config
            if save_object(get_request(), "agreement", insert=True):
                LOGGER.info(
                    f"Created agreement {agreement['_id']}",
                    extra=context_unpack(
                        get_request(),
                        {"MESSAGE_ID": "agreement_create"},
                        {
                            "agreement_id": agreement['_id'],
                            "agreement_mode": agreement.get('mode')
                        },
                    ),
                )

                framework = deepcopy(framework_data)
                framework["agreementID"] = agreement['_id']
                get_request().validated["framework"] = framework
                save_object(get_request(), "framework")
                LOGGER.info(
                    f"Updated framework {framework_data['_id']} with agreementID",
                    extra=context_unpack(get_request(), {"MESSAGE_ID": "framework_patch"}),
                )

    def create_agreement_contract(self):
        qualification = get_request().validated["qualification"]
        framework = get_request().validated["framework"]
        agreement_data = get_agreement_by_id(get_request(), framework["agreementID"])
        if not agreement_data:
            raise_operation_error(
                get_request(),
                "agreementID must be one of exists agreement",
            )
        submission_data = get_submission_by_id(get_request(), qualification["submissionID"])
        if not agreement_data:
            raise_operation_error(
                get_request(),
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
            "qualificationID": qualification["_id"],
            "submissionID": submission_data["_id"],
            "status": "active",
            "suppliers": submission_data["tenderers"],
            "milestones": [first_milestone_data],
        }

        if "contracts" not in agreement_data:
            agreement_data["contracts"] = []
        agreement_data["contracts"].append(contract_data)


        model = get_request().agreement_from_data(agreement_data, create=False)
        agreement = model(agreement_data)
        get_request().validated["agreement"] = agreement.serialize()

        if save_object(get_request(), "agreement"):
            LOGGER.info(
                f"Updated agreement {agreement_data['_id']} with contract {contract_id}",
                extra=context_unpack(
                    get_request(),
                    {"MESSAGE_ID": "qualification_patch"},
                ),
            )
