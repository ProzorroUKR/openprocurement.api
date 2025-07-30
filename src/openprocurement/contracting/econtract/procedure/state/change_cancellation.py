from openprocurement.contracting.econtract.procedure.state.contract_cancellation import (
    CancellationState,
)


class ChangeCancellationState(CancellationState):
    def cancellation_on_post(self, data):
        change = self.request.validated["change"]
        self.set_author_of_object(data)
        data["status"] = "active"
        self.set_object_status(change, "cancelled")
