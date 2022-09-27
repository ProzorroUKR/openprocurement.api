from openprocurement.tender.core.procedure.state.contract import ContractStateMixing
from openprocurement.tender.open.procedure.state.tender import OpenTenderState


class OpenContractStateMixing(ContractStateMixing):
    def contract_on_patch(self, before: dict, after: dict):
        self.validate_contract_items(before, after)
        self.validate_contract_signing(before, after)
        super().contract_on_patch(before, after)


class OpenContractState(OpenContractStateMixing, OpenTenderState):
    pass
