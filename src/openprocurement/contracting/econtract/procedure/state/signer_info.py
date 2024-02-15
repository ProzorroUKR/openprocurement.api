from openprocurement.contracting.econtract.procedure.state.contract import (
    EContractState,
)


class EContractSignerInfoState(EContractState):
    def signer_info_on_put(self, data: dict) -> None:
        tender = self.request.validated["tender"]
        award = self.request.validated["award"]
        self.validate_cancellation_blocks(self.request, tender, lot_id=award.get("lotID"))
