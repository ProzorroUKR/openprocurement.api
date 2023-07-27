from logging import getLogger


from openprocurement.contracting.core.procedure.state.contract import ContractState
from openprocurement.api.utils import raise_operation_error
from openprocurement.tender.pricequotation.procedure.state.contract import PQContractState

LOGGER = getLogger(__name__)


class EContractState(ContractState):
    terminated_statuses = ("terminated", "cancelled")

    def always(self, data) -> None:
        super().always(data)

    def status_up(self, before, after, data):
        super().status_up(before, after, data)
        if before != "active" and after == "active":
            self.validate_required_signed_info(data)
        self.synchronize_contracts(data)

    def validate_required_signed_info(self, data):
        supplier_signer_info = all(i.get("signerInfo") for i in data.get("suppliers", ""))
        if not data.get("buyer", {}).get("signerInfo") or not supplier_signer_info:
            raise_operation_error(
                self.request,
                f"signerInfo field for buyer and suppliers "
                f"is required for contract in `{data.get('status')}` status",
                status=422
            )

    def synchronize_contracts(self, data):
        pass
