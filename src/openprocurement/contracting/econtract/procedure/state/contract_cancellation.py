from openprocurement.api.utils import raise_operation_error
from openprocurement.contracting.econtract.procedure.models.cancellation import PostContractCancellation
from openprocurement.contracting.econtract.procedure.state.contract import (
    EContractState,
)


class CancellationState(EContractState):
    post_data_model = PostContractCancellation

    # --- request validation (called from the views) ---

    def validate_cancellation_post_request(self):
        if self.request.authenticated_role not in ("Administrator", "admins"):
            self.validate_contract_participant()
        self.validate_input_data(self.get_post_data_model())
        self.validate_contract_status_pending()

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
