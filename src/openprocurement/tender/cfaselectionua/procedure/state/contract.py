from openprocurement.tender.core.procedure.state.contract import ContractStateMixing
from openprocurement.tender.cfaselectionua.procedure.state.tender import CFASelectionTenderState
from openprocurement.api.utils import (
    get_now,
    context_unpack,
)
from openprocurement.tender.core.procedure.utils import contracts_allow_to_complete
from logging import getLogger
from datetime import datetime

LOGGER = getLogger(__name__)


class CFASelectionContractState(ContractStateMixing, CFASelectionTenderState):
    def check_agreements(self, tender: dict) -> bool:
        return False

    def check_award_lot_complaints(self, tender: dict, lot_id: str, lot_awards: list, now: datetime) -> bool:
        return True

    def check_award_complaints(self, tender: dict, now: datetime) -> None:
        last_award_status = tender.get("awards", [])[-1].get("status") if tender.get("awards", []) else ""
        if last_award_status == "unsuccessful":
            LOGGER.info(
                f"Switched tender {tender['id']} to unsuccessful",
                extra=context_unpack(self.request, {"MESSAGE_ID": "switched_tender_unsuccessful"}),
            )
            self.set_object_status(tender, "unsuccessful")

        contracts = tender.get("contracts", [])
        allow_complete_tender = contracts_allow_to_complete(contracts)
        if allow_complete_tender:
            self.set_object_status(tender, "complete")

    def check_tender_status_method(self) -> None:
        tender = self.request.validated["tender"]
        now = get_now()
        if tender.get("lots"):
            self.check_lots_complaints(tender, now)
        else:
            self.check_award_complaints(tender, now)

    def contract_on_patch(self, before: dict, after: dict):
        self.validate_contract_items(before, after)
        super().contract_on_patch(before, after)
