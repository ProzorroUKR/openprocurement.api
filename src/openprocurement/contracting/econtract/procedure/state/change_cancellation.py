from openprocurement.contracting.econtract.procedure.models.cancellation import PostCancellation
from openprocurement.contracting.econtract.procedure.state.contract_cancellation import (
    CancellationState,
)


class ChangeCancellationState(CancellationState):
    post_data_model = PostCancellation

    # --- request validation (called from the views) ---

    def validate_cancellation_post_request(self):
        if self.request.authenticated_role not in ("Administrator", "admins"):
            self.validate_contract_participant()
        self.validate_input_data(self.get_post_data_model())
        self.validate_contract_change_allowed()
        self.validate_contract_change_update_allowed()

    def cancellation_on_post(self, data):
        change = self.request.validated["change"]
        self.set_author_of_object(data)
        data["status"] = "active"
        self.set_object_status(change, "cancelled")
