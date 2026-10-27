from openprocurement.api.utils import raise_operation_error
from openprocurement.api.validation import OPERATIONS
from openprocurement.framework.core.procedure.models.contract import (
    Contract,
    PatchContract,
)
from openprocurement.framework.core.procedure.state.agreement import AgreementState


class ContractState(AgreementState):
    patch_data_model = PatchContract
    data_model = Contract

    # --- request validation (called from the views) ---

    def validate_contract_patch_request(self):
        self.validate_item_owner("framework")
        self.validate_patch_input_data(self.get_patch_data_model())
        self.validate_patch_data(self.get_data_model(), item_name="contract")
        self.validate_agreement_status()

    def get_patch_data_model(self):
        return self.patch_data_model

    def validate_contract_status(self, obj_name="object"):
        status = self.request.validated["contract"]["status"]
        if status not in ("active", "suspended"):
            raise_operation_error(
                self.request,
                f"Can't {OPERATIONS.get(self.request.method)} {obj_name} in current ({status}) contract status",
            )
