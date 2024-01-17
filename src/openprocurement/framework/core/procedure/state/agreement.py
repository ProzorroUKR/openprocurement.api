from logging import getLogger
from hashlib import sha512
from openprocurement.api.context import get_request, get_now
from openprocurement.api.procedure.context import init_object
from openprocurement.api.utils import generate_id, context_unpack
from openprocurement.framework.core.procedure.models.agreement import (
    PatchAgreement,
    AgreementChronographData,
)
from openprocurement.framework.core.procedure.serializers.agreement import AgreementConfigSerializer
from openprocurement.framework.core.procedure.state.chronograph import ChronographEventsMixing
from openprocurement.framework.core.utils import generate_agreement_id
from openprocurement.tender.core.procedure.state.base import BaseState

LOGGER = getLogger(__name__)


def get_agreement_next_check(data):
    checks = []
    if data["status"] == "active":
        milestone_due_dates = [
            milestone["dueDate"]
            for contract in data.get("contracts", []) for milestone in contract.get("milestones", [])
            if milestone.get("dueDate") and milestone["status"] == "scheduled"
        ]
        if milestone_due_dates:
            checks.append(min(milestone_due_dates))
        checks.append(data["period"]["endDate"])
    return min(checks) if checks else None


class AgreementState(BaseState, ChronographEventsMixing):

    def __init__(self, request, framework=None):
        super().__init__(request)
        self.framework = framework

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
        return get_agreement_next_check(data)

    def create_agreement_if_not_exist(self):
        request = self.request
        framework_config = request.validated["framework_config"]
        framework_data = request.validated["framework"]
        if "agreement" not in request.validated:
            now = get_now().isoformat()
            transfer = generate_id()
            transfer_token = sha512(transfer.encode("utf-8")).hexdigest()
            agreement = {
                "id": generate_id(),
                "agreementID": generate_agreement_id(request),
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
                "config": {
                    "test": framework_config.get("test", False),
                    "restricted": framework_config.get("restrictedDerivatives", False),
                },
            }

            init_object(
                "agreement",
                agreement,
                obj_src={},
                config_serializer=AgreementConfigSerializer,
            )

            # update framework
            request.validated["framework"]["agreementID"] = agreement['id']

    def create_agreement_contract(self):
        request = self.request
        qualification = request.validated["qualification"]
        framework = request.validated["framework"]
        agreement_data = request.validated["agreement"]
        submission = request.validated["submission"]

        if agreement_data["status"] != "active":
            LOGGER.error(
                f"Agreement {framework['agreementID']} is not active",
                extra=context_unpack(
                    request,
                    {"MESSAGE_ID": "qualification_patch_error"},
                ),
            )
            return

        contract_id = generate_id()
        first_milestone_data = {
            "id": generate_id(),
            "status": "scheduled",
            "type": "activation",
            "dueDate": framework.get("qualificationPeriod").get("endDate"),
            "dateModified": get_now().isoformat(),
        }
        contract_data = {
            "id": contract_id,
            "qualificationID": qualification["_id"],
            "submissionID": submission["_id"],
            "status": "active",
            "suppliers": submission["tenderers"],
            "milestones": [first_milestone_data],
            "date": get_now().isoformat(),
        }

        if "contracts" not in agreement_data:
            agreement_data["contracts"] = []
        agreement_data["contracts"].append(contract_data)

        LOGGER.info(
            f"Updated agreement {framework['agreementID']} with contract {contract_id}",
            extra=context_unpack(
                request,
                {"MESSAGE_ID": "qualification_patch"},
            ),
        )
