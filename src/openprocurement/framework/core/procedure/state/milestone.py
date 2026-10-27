from logging import getLogger

from openprocurement.api.context import get_request, get_request_now
from openprocurement.api.utils import raise_operation_error
from openprocurement.api.validation import OPERATIONS
from openprocurement.framework.core.constants import MILESTONE_CONTRACT_STATUSES
from openprocurement.framework.core.procedure.models.milestone import Milestone, PatchMilestone, PostMilestone
from openprocurement.framework.core.procedure.state.contract import ContractState

LOGGER = getLogger(__name__)


class MilestoneState(ContractState):
    post_data_model = PostMilestone
    patch_data_model = PatchMilestone
    data_model = Milestone

    # --- request validation (called from the views) ---

    def validate_milestone_post_request(self):
        self.validate_item_owner("framework")
        self.validate_input_data(self.get_post_data_model())
        self.validate_agreement_status()
        self.validate_contract_status()
        self.validate_milestone_contract_suspended()
        self.validate_milestone_type()
        self.validate_data_documents(route_key="milestone_id", uid_key="id")

    def validate_milestone_patch_request(self):
        self.validate_item_owner("framework")
        self.validate_patch_input_data(self.get_patch_data_model())
        self.validate_patch_data(self.get_data_model(), item_name="milestone")
        self.validate_agreement_status()
        self.validate_contract_status()
        self.validate_milestone_contract_suspended()
        self.validate_milestone_patch_type()
        self.validate_milestone_scheduled()
        self.validate_milestone_status_change()

    def validate_milestone_contract_suspended(self):
        """only an activation milestone can be added / changed for a suspended contract"""
        milestone_type = self.request.validated["data"].get("type")
        if (
            milestone_type
            and self.request.validated["contract"]["status"] == "suspended"
            and milestone_type != "activation"
        ):
            raise_operation_error(
                self.request,
                f"Can't {OPERATIONS.get(self.request.method)} {milestone_type} milestone for contract in suspended status",
            )

    def validate_milestone_type(self):
        if self.request.validated["data"].get("type") == "activation":
            raise_operation_error(
                self.request,
                f"Can't {OPERATIONS.get(self.request.method)} object for 'activation' milestone",
            )

    def validate_milestone_patch_type(self):
        milestone_type = self.request.validated["milestone"]["type"]
        if milestone_type != "activation":
            raise_operation_error(self.request, f"Can't patch `{milestone_type}` milestone")

    def validate_milestone_scheduled(self, obj_name="milestone"):
        status = self.request.validated["milestone"]["status"]
        if status != "scheduled":
            raise_operation_error(
                self.request,
                f"Can't {OPERATIONS.get(self.request.method)} {obj_name} in current ({status}) status",
            )

    def validate_milestone_status_change(self):
        curr_status = self.request.validated["milestone"]["status"]
        new_status = self.request.validated["data"].get("status", curr_status)
        if curr_status != new_status and new_status != "met":
            raise_operation_error(
                self.request,
                f"Can't switch milestone status from `{curr_status}` to `{new_status}`",
            )

    def on_post(self, data):
        contract = get_request().validated["contract"]
        contract["date"] = contract["dateModified"] = data["dateModified"] = get_request_now().isoformat()
        self.set_contract_status_on_post(data)
        super().on_post(data)

    def on_patch(self, before, after):
        self.update_contract_status_on_patch(after)
        now = get_request_now().isoformat()
        contract = get_request().validated["contract"]
        after["dateModified"] = contract["dateModified"] = now
        super().on_patch(before, after)

    def set_agreement_data(self, data):
        pass

    def update_contract_status_on_patch(self, data):
        if data["status"] == "met":
            now = get_request_now().isoformat()
            data["dateMet"] = now
            contract = get_request().validated["contract"]
            contract["status"] = "terminated"
            contract["date"] = contract["dateModified"] = now
            for milestone in contract["milestones"]:
                if milestone["status"] == "scheduled":
                    milestone["status"] = "notMet"
                    milestone["dateModified"] = now

    def set_contract_status_on_post(self, data):
        contract = get_request().validated["contract"]
        contract["status"] = MILESTONE_CONTRACT_STATUSES[data["type"]]
