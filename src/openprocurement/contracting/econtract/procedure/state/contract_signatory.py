from copy import deepcopy

from openprocurement.api.context import get_request_now
from openprocurement.api.utils import raise_operation_error
from openprocurement.contracting.core.procedure.state.contract import (
    ContractState as BaseContractState,
)


class SignatoryState(BaseContractState):
    def signatory_on_post(self, data):
        self.validate_contract_is_ready_for_activation()
        self.set_author_of_object(data, "role")
        data["date"] = get_request_now().isoformat()
        self._validate_signatory_exists(data)
        self._validate_signatures_count(data)
        self.activate_contract_if_all_signed(data)

    def _validate_signatory_exists(self, data):
        contract = self.request.validated["contract"]

        # validate already existing signatory
        if [x for x in contract.get("signatories", []) if x["role"] == data["role"]]:
            raise_operation_error(
                self.request,
                f"Signatory by {data['role']} was already created.",
                name="signatories",
                status=422,
            )

    def _validate_signatures_count(self, data):
        contract = self.request.validated["contract"]

        if data["role"] == "supplier":
            required_count = len(contract.get("suppliers", []))
        else:
            required_count = 1

        signs_count = len(
            [
                doc
                for doc in contract.get("documents", [])
                if doc.get("documentType") == "contractSignature" and doc.get("author") == data["role"]
            ]
        )

        # validate required contractSignature count
        if signs_count < required_count:
            raise_operation_error(
                self.request,
                f"Not enough contractSignature documents by {data['role']} were uploaded.",
                name="documents",
                status=422,
            )

    def validate_contract_is_ready_for_activation(self):
        tender = self.request.validated["tender"]
        contract = self.request.validated["contract"]
        contract["id"] = contract["_id"]
        contract_after = deepcopy(contract)
        self.set_object_status(contract_after, "active")

        self.validate_required_signed_info(contract)
        self.validate_contract_pending_patch(self.request, contract, contract_after)
        self.validate_contract_active_patch(self.request, contract, contract_after)
        self.validate_activate_contract(contract)
        self.validate_activate_contract_with_review_request(
            self.request,
            tender,
            contract_after,
            self.request.validated["award"].get("lotID"),
        )

    def activate_contract_if_all_signed(self, data):
        contract = self.request.validated["contract"]
        signatories = contract.get("signatories", []) + [data]

        buyer_signatories = [x for x in signatories if x["role"] == "buyer"]
        supplier_signatories = [x for x in signatories if x["role"] == "supplier"]

        if buyer_signatories and supplier_signatories:
            self.set_object_status(contract, "active")
            contract_changed = self.synchronize_contracts_data(contract)
            if contract.get("dateSigned", None) is None:
                contract["dateSigned"] = get_request_now().isoformat()
            self.check_tender_status_method()
            self.request.validated["contract_was_changed"] = contract_changed
