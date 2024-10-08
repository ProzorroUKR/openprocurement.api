from logging import getLogger

from openprocurement.api.context import get_now, get_request
from openprocurement.framework.core.constants import MILESTONE_CONTRACT_STATUSES
from openprocurement.framework.core.procedure.state.agreement import AgreementState

LOGGER = getLogger(__name__)


class MilestoneState(AgreementState):
    def on_post(self, data):
        get_request().validated["contract"]["date"] = data["dateModified"] = get_now().isoformat()
        self.set_contract_status_on_post(data)
        super().on_post(data)

    def on_patch(self, before, after):
        self.update_contract_status_on_patch(after)
        super().on_patch(before, after)

    def set_agreement_data(self, data):
        pass

    def update_contract_status_on_patch(self, data):
        if data["status"] == "met":
            contract = get_request().validated["contract"]
            contract["status"] = "terminated"
            for milestone in contract["milestones"]:
                if milestone["status"] == "scheduled":
                    milestone["status"] = "notMet"

    def set_contract_status_on_post(self, data):
        contract = get_request().validated["contract"]
        contract["status"] = MILESTONE_CONTRACT_STATUSES[data["type"]]
