from openprocurement.tender.core.procedure.state.contract import ContractState


class OpenUAContractState(ContractState):

    def on_patch(self, before: dict, after: dict):
        self.validate_contract_items(before, after)
        self.validate_contract_signing(after)
        super().on_patch(before, after)
