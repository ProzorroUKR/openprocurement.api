from logging import getLogger

from openprocurement.api.context import get_request, get_request_now
from openprocurement.framework.core.constants import MILESTONE_CONTRACT_STATUSES
from openprocurement.framework.core.procedure.state.agreement import AgreementState

LOGGER = getLogger(__name__)


class MilestoneState(AgreementState):
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
