from openprocurement.tender.core.procedure.state.contract import ContractState
from openprocurement.tender.belowthreshold.procedure.state.tender import BelowThresholdTenderState


class BelowThresholdContractState(ContractState):

    def check_tender_status_method(self) -> None:
        super().check_tender_status_method()
        tender = self.request.validated["tender"]
        BelowThresholdTenderState.check_ignored_claim(tender)

    def check_skip_award_complaint_period(self, procurementMethodRationale: str) -> bool:
        return procurementMethodRationale == "simple"

    def on_patch(self, before: dict, after: dict):
        self.validate_contract_items(before, after)
        self.validate_contract_signing(after)
        super().on_patch(before, after)
