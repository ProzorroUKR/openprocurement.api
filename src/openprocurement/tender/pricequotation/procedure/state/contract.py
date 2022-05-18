from openprocurement.tender.core.procedure.state.contract import ContractState
from openprocurement.api.utils import context_unpack
from logging import getLogger

LOGGER = getLogger(__name__)


class PQContractState(ContractState):

    def check_tender_status_method(self) -> None:
        tender = self.request.validated["tender"]
        last_award_status = tender["awards"][-1]["status"] if tender.get("awards") else ""
        if last_award_status == "unsuccessful":
            LOGGER.info(
                f"Switched tender {tender['id']} to unsuccessful",
                extra=context_unpack(
                    self.request,
                    {"MESSAGE_ID": "switched_tender_unsuccessful"}
                ),
            )
            tender["status"] = "unsuccessful"
        if (
                tender.get("contracts")
                and any([contract["status"] == "active" for contract in tender["contracts"]])
                and not any([contract["status"] == "pending" for contract in tender["contracts"]])
        ):
            tender["status"] = "complete"

    def on_patch(self, before: dict, after: dict):
        self.validate_contract_items(before, after)
        super().on_patch(before, after)
