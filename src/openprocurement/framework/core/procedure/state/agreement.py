from hashlib import sha512
from logging import getLogger

from openprocurement.api.context import get_request, get_request_now
from openprocurement.api.procedure.context import get_framework
from openprocurement.api.procedure.state.base import BaseState
from openprocurement.api.procedure.validation import validate_patch_input_data_from_resolved_model
from openprocurement.api.utils import (
    context_unpack,
    generate_id,
    get_framework_by_id,
    raise_operation_error,
    request_init_agreement,
    request_init_framework,
)
from openprocurement.api.validation import OPERATIONS
from openprocurement.framework.core.procedure.models.agreement import (
    AgreementChronographData,
    PatchAgreement,
)
from openprocurement.framework.core.procedure.state.chronograph import (
    AgreementChronographEventsMixing,
)
from openprocurement.framework.core.utils import generate_agreement_id

LOGGER = getLogger(__name__)


class AgreementState(BaseState, AgreementChronographEventsMixing):
    # data_model: the agreement model of the procedure
    patch_data_model = PatchAgreement

    def __init__(self, request, framework=None):
        super().__init__(request)
        self.framework = framework

    # --- request validation (called from the views) ---

    def validate_agreement_patch_request(self):
        validate_patch_input_data_from_resolved_model()(self.request)
        self.validate_patch_data(self.get_data_model(), item_name="agreement")
        self.fetch_agreement_framework()
        if self.request.authenticated_role not in ("chronograph", "Administrator"):
            self.validate_agreement_status()

    def fetch_agreement_framework(self):
        """the framework of the agreement (request.validated["framework"])"""
        request = self.request
        framework_id = request.validated["data"].get("frameworkID", request.validated["agreement"].get("frameworkID"))
        request_init_framework(request, get_framework_by_id(request, framework_id))

    def validate_agreement_status(self, obj_name="object"):
        status = self.request.validated["agreement"]["status"]
        if status != "active":
            raise_operation_error(
                self.request,
                f"Can't {OPERATIONS.get(self.request.method)} {obj_name} in current ({status}) agreement status",
            )

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
        if self.request.authenticated_role == "chronograph":
            return AgreementChronographData
        return self.patch_data_model

    def create_agreement_if_not_exist(self):
        request = self.request
        framework = get_framework()

        if "agreement" not in request.validated:
            now = get_request_now().isoformat()
            transfer = generate_id()
            transfer_token = sha512(transfer.encode("utf-8")).hexdigest()
            agreement = {
                "id": generate_id(),
                "agreementID": generate_agreement_id(request),
                "frameworkID": framework["_id"],
                "agreementType": framework["frameworkType"],
                "status": "active",
                "period": {
                    "startDate": now,
                    "endDate": framework.get("qualificationPeriod").get("endDate"),
                },
                "procuringEntity": framework.get("procuringEntity"),
                "classification": framework.get("classification"),
                "additionalClassifications": framework.get("additionalClassifications"),
                "contracts": [],
                "owner": framework["owner"],
                "owner_token": framework["owner_token"],
                "mode": framework.get("mode"),
                "dateModified": now,
                "date": now,
                "transfer_token": transfer_token,
                "frameworkDetails": framework.get("frameworkDetails"),
                "config": {
                    "restricted": framework["config"].get("restrictedDerivatives", False),
                },
            }
            if "items" in framework:
                agreement["items"] = framework["items"]

            request_init_agreement(request, agreement, agreement_src={})

            # update framework
            framework["agreementID"] = agreement["id"]

    def create_agreement_contract(self):
        request = self.request
        qualification = request.validated["qualification"]
        framework = request.validated["framework"]
        agreement = request.validated["agreement"]
        submission = request.validated["submission"]

        if agreement["status"] != "active":
            LOGGER.error(
                f"Agreement {framework['agreementID']} is not active",
                extra=context_unpack(
                    request,
                    {"MESSAGE_ID": "qualification_patch_error"},
                ),
            )
            return

        contract_id = generate_id()
        now = get_request_now().isoformat()
        first_milestone = {
            "id": generate_id(),
            "status": "scheduled",
            "type": "activation",
            "dueDate": framework.get("qualificationPeriod").get("endDate"),
            "dateModified": now,
        }
        contract = {
            "id": contract_id,
            "qualificationID": qualification["_id"],
            "submissionID": submission["_id"],
            "status": "active",
            "suppliers": submission["tenderers"],
            "milestones": [first_milestone],
            "date": now,
            "dateModified": now,
        }

        if "contracts" not in agreement:
            agreement["contracts"] = []
        agreement["contracts"].append(contract)

        LOGGER.info(
            f"Updated agreement {framework['agreementID']} with contract {contract_id}",
            extra=context_unpack(
                request,
                {"MESSAGE_ID": "qualification_patch"},
            ),
        )
