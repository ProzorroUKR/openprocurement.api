from openprocurement.api.context import get_now
from openprocurement.api.utils import raise_operation_error
from openprocurement.contracting.core.procedure.state.contract import BaseContractState
from openprocurement.contracting.core.procedure.utils import is_bid_owner
from openprocurement.tender.core.procedure.models.milestone import TenderMilestoneTypes


class ContractMilestoneState(BaseContractState):
    def on_patch(self, before, after):
        self.validate_milestone_patch_role(before)
        if before["status"] == "met":
            raise_operation_error(
                self.request,
                "Milestone already met",
                status=422,
            )
        if before["status"] != after["status"]:
            after["dateMet"] = get_now().isoformat()
        super().on_patch(before, after)

    def validate_milestone_patch_role(self, milestone):
        contract = self.request.validated["contract"]
        if is_bid_owner(self.request, contract):
            if milestone["type"] != TenderMilestoneTypes.FINANCING.value:
                raise_operation_error(
                    self.request,
                    f"Supplier can update only {TenderMilestoneTypes.FINANCING.value} milestones",
                    location="url",
                    name="role",
                )
        elif milestone["type"] != TenderMilestoneTypes.DELIVERY.value:
            raise_operation_error(
                self.request,
                f"Buyer can update only {TenderMilestoneTypes.DELIVERY.value} milestones",
                location="url",
                name="role",
            )
