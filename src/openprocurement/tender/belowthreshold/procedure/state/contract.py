from openprocurement.tender.core.procedure.state.contract import ContractStateMixing
from openprocurement.tender.belowthreshold.procedure.state.tender import BelowThresholdTenderState


class BelowThresholdContractState(ContractStateMixing, BelowThresholdTenderState):

    def check_tender_status_method(self) -> None:
        super().check_tender_status_method()
        tender = self.request.validated["tender"]
        self.check_ignored_claim(tender)

    def check_skip_award_complaint_period(self, pmr: str) -> bool:
        return pmr == "simple"

    def contract_on_patch(self, before: dict, after: dict):
        self.validate_contract_items(before, after)
        self.validate_contract_signing(before, after)
        super().contract_on_patch(before, after)
