from openprocurement.contracting.core.procedure.state.contract import ContractState
from openprocurement.contracting.core.procedure.utils import get_tender_award_by_contract


class ContractSignerInfoState(ContractState):
    def signer_info_on_put(self, data: dict) -> None:
        tender = self.request.validated["tender"]
        award = get_tender_award_by_contract(tender, self.request.validated["contract"])
        self.validate_cancellation_blocks(self.request, tender, lot_id=award.get("lotID"))
