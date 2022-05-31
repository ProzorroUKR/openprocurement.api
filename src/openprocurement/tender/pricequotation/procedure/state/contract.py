from openprocurement.tender.core.procedure.state.contract import ContractStateMixing
from openprocurement.tender.pricequotation.procedure.state.tender import PriceQuotationTenderState
from openprocurement.api.utils import context_unpack
from logging import getLogger

LOGGER = getLogger(__name__)


class PQContractState(ContractStateMixing, PriceQuotationTenderState):

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
            self.set_object_status(tender, "unsuccessful")
        if (
                tender.get("contracts")
                and any([contract["status"] == "active" for contract in tender["contracts"]])
                and not any([contract["status"] == "pending" for contract in tender["contracts"]])
        ):
            self.set_object_status(tender, "complete")

    def contract_on_patch(self, before: dict, after: dict):
        self.validate_contract_items(before, after)
        super().contract_on_patch(before, after)
