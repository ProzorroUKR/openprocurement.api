from copy import deepcopy

from openprocurement.api.utils import raise_operation_error
from openprocurement.contracting.core.procedure.state.contract import (
    ContractState as BaseContractState,
)
from openprocurement.tender.core.procedure.contracting import (
    upload_contract_change_pdf_document,
)


class EChangeState(BaseContractState):
    def change_on_post(self, data):
        self.validate_change(data)
        self.set_author_of_object(data)
        contract = self.request.validated["contract"]
        tender = self.request.validated["tender"]
        upload_contract_change_pdf_document(data, contract, tender)

    def validate_change(self, data):
        # we will work with deepcopy of contract, as we don't want to apply any changes to contract directly,
        # but we need actual version of contract for next validations with all previous active changes modifications
        contract = deepcopy(self.request.validated["contract"])
        self.apply_previous_changes(contract)
        self.validate_modifications(contract, data)
        data_for_validation = deepcopy(data["modifications"])
        if "items" in data_for_validation:
            self.validate_patch_contract_items(self.request, contract, data_for_validation)
        self.validate_update_contract_value(self.request, contract, data_for_validation)
        self.validate_update_contract_value_net_required(self.request, contract, data_for_validation)
        self.validate_update_contract_value_amount(self.request, contract, data_for_validation)

        # for next validations we must have these fields for comparing
        for field_name in ("value", "amountPaid", "period", "items"):
            if field_name not in data_for_validation:
                data_for_validation[field_name] = contract.get(field_name)

        self.validate_contract_active_patch(self.request, contract, data_for_validation)
        self.validate_activate_contract(data_for_validation)

        # in validate_period empty fields filled from contract, we need them to have full period in change.modifications
        if "period" in data["modifications"]:
            data["modifications"]["period"] = data_for_validation["period"]

        # synchronize real data["modifications"], not copy for previous validations
        self.synchronize_items_unit_value(data["modifications"], contract.get("value"))

    @staticmethod
    def apply_previous_changes(contract):
        for change in contract.get("changes"):
            if change["status"] == "active":
                contract.update(change["modifications"])

    def validate_modifications(self, contract, data):
        if not data.get("modifications"):
            raise_operation_error(
                self.request,
                "Contract modifications are empty",
                status=422,
                name="modifications",
            )
        # check if there are any changes
        updated_contract_data = {}
        for f, v in data["modifications"].items():
            if contract.get(f) != v:
                updated_contract_data[f] = v
        if not updated_contract_data:
            raise_operation_error(
                self.request,
                "No changes detected between contract and current modifications",
                status=422,
            )
