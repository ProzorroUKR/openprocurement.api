from openprocurement.tender.core.procedure.state.contract import ContractStateMixing
from openprocurement.tender.openua.procedure.state.tender import OpenUATenderState


class OpenUAContractState(ContractStateMixing, OpenUATenderState):

    def contract_on_patch(self, before: dict, after: dict):
        self.validate_contract_items(before, after)
        self.validate_contract_signing(before, after)
        super().contract_on_patch(before, after)
