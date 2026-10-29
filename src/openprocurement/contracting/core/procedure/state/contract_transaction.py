from openprocurement.api.procedure.state.base import BaseState
from openprocurement.contracting.core.procedure.models.transaction import PutTransaction
from openprocurement.contracting.core.procedure.state.contract import ContractRequestRulesMixin

TRANSACTION_STATUS_MAP = {
    "0": "successful",
    "-1": "canceled",
}


class TransactionState(ContractRequestRulesMixin, BaseState):
    post_data_model = PutTransaction

    # --- request validation (called from the views) ---

    def validate_transaction_put_request(self):
        if self.request.authenticated_role not in ("bots", "admins"):
            self.validate_contract_owner()
        self.validate_input_data(self.get_post_data_model())

    def transaction_on_put(self, data):
        _status_value = data["status"]
        data["status"] = TRANSACTION_STATUS_MAP.get(_status_value, _status_value)
