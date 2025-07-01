from openprocurement.api.utils import raise_operation_error
from openprocurement.contracting.core.procedure.state.contract import (
    ContractState as BaseContractState,
)


class EContractState(BaseContractState):
    def on_patch(self, before, after) -> None:
        if after["status"] == "pending" and any(
            doc.get("documentType") == "contractSignature" for doc in before.get("documents", [])
        ):
            raise_operation_error(
                self.request,
                f"Forbidden to patch already signed contract in status {after['status']}",
            )
        super().on_patch(before, after)

    def status_up(self, before: str, after: str, data: dict) -> None:
        super().status_up(before, after, data)
        if before != "active" and after == "active":
            self.validate_required_all_participants_signatures(data)

    def validate_required_all_participants_signatures(self, data: dict) -> None:
        suppliers_count = len(data.get("suppliers", []))
        participants_count = suppliers_count + 1  # all suppliers + buyer signature
        signs_count = len([doc for doc in data.get("documents", []) if doc.get("documentType") == "contractSignature"])
        if signs_count != participants_count:
            raise_operation_error(
                self.request,
                f"contractSignature document type for all participants "
                f"is required for contract in `{data.get('status')}` status",
                status=422,
            )
