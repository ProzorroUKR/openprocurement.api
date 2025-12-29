from openprocurement.api.context import get_request_now
from openprocurement.api.utils import raise_operation_error
from openprocurement.contracting.core.procedure.state.contract import (
    ContractState as BaseContractState,
)


class SignatoryState(BaseContractState):
    def signatory_on_post(self, data):
        self.set_author_of_object(data, "role")
        data["date"] = get_request_now().isoformat()
        self._validate_signatory_exists(data)
        self._validate_signatures_count(data)
        self.activate_change_if_all_signed(data)

    def _validate_signatory_exists(self, data):
        change = self.request.validated["change"]

        # validate already existing signatory
        if [x for x in change.get("signatories", []) if x["role"] == data["role"]]:
            raise_operation_error(
                self.request,
                f"Signatory by {data['role']} was already created.",
                name="signatories",
                status=422,
            )

    def _validate_signatures_count(self, data):
        change = self.request.validated["change"]

        if data["role"] == "supplier":
            required_count = len(self.request.validated["contract"].get("suppliers", []))
        else:
            required_count = 1

        signs_count = len(
            [
                doc
                for doc in change.get("documents", [])
                if doc.get("documentType") == "contractSignature" and doc.get("author") == data["role"]
            ]
        )

        if signs_count < required_count:
            raise_operation_error(
                self.request,
                f"Not enough contractSignature documents by {data['role']} were uploaded.",
                name="documents",
                status=422,
            )

    def activate_change_if_all_signed(self, data):
        change = self.request.validated["change"]
        signatories = change.get("signatories", []) + [data]

        buyer_signatories = [x for x in signatories if x["role"] == "buyer"]
        supplier_signatories = [x for x in signatories if x["role"] == "supplier"]

        if buyer_signatories and supplier_signatories:
            self.set_object_status(change, "active")
            change["dateSigned"] = get_request_now().isoformat()
