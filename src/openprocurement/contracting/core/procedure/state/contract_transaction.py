from openprocurement.api.procedure.state.base import BaseState

TRANSACTION_STATUS_MAP = {
    "0": "successful",
    "-1": "canceled",
}


class TransactionState(BaseState):
    def transaction_on_put(self, data):
        _status_value = data["status"]
        data["status"] = TRANSACTION_STATUS_MAP.get(_status_value, _status_value)
