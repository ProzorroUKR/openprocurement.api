from openprocurement.api.utils import raise_operation_error
from openprocurement.contracting.econtract.procedure.state.contract import (
    EContractState,
)


class CancellationState(EContractState):
    def cancellation_on_post(self, data):
        contract = self.request.validated["contract"]
        self.set_author_of_object(data)
        self.validate_pending_cancellation_existed(contract)

    def validate_pending_cancellation_existed(self, contract):
        for prev_obj in contract.get("cancellations", []):
            if prev_obj.get("status") == "pending":
                raise_operation_error(
                    self.request,
                    "Cancellation for contract already exists",
                )
