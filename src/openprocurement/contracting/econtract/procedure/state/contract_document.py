from copy import deepcopy

from openprocurement.api.context import get_request_now
from openprocurement.api.utils import raise_operation_error
from openprocurement.contracting.core.procedure.state.document import (
    ContractDocumentState as BaseContractDocumentState,
)


class EContractDocumentState(BaseContractDocumentState):
    def validate_document_post(self, data):
        super().validate_document_post(data)
        if data.get("documentType") == "contractSignature":
            self.validate_contract_cancellations()
            self.validate_contract_is_ready_for_signing()
            self.set_author_of_object(data)
            self.validate_contract_signature_duplicate(data)

    def document_on_post(self, data):
        super().document_on_post(data)
        self.activate_contract_if_signed(data)

    def validate_contract_cancellations(self):
        contract = self.request.validated["contract"]
        if contract.get("cancellations", []):
            raise_operation_error(
                self.request,
                "Forbidden to sign contract with cancellation",
            )

    def validate_contract_is_ready_for_signing(self):
        tender = self.request.validated["tender"]
        contract = self.request.validated["contract"]
        contract["id"] = contract["_id"]
        contract_after = deepcopy(contract)
        self.set_object_status(contract_after, "active")

        self.validate_required_signed_info(contract)
        self.validate_required_fields_before_activation(contract)
        self.validate_contract_pending_patch(self.request, contract, contract_after)
        self.validate_contract_active_patch(self.request, contract, contract_after)
        self.validate_activate_contract(contract)
        self.validate_activate_contract_with_review_request(
            self.request,
            tender,
            contract_after,
            self.request.validated["award"].get("lotID"),
        )

    def activate_contract_if_signed(self, doc):
        contract = self.request.validated["contract"]

        docs = deepcopy(contract.get("documents", []))
        docs.append(doc)

        suppliers_count = len(contract.get("suppliers", []))
        participants_count = suppliers_count + 1  # all suppliers + buyer signature
        signs_count = len([doc for doc in docs if doc.get("documentType") == "contractSignature"])
        if signs_count == participants_count:
            self.set_object_status(contract, "active")
            contract_changed = self.synchronize_contracts_data(contract)
            if contract.get("dateSigned", None) is None:
                contract["dateSigned"] = get_request_now().isoformat()
            self.check_tender_status_method()
            self.request.validated["contract_was_changed"] = contract_changed

    def validate_document_patch(self, before, after):
        super().validate_document_patch(before, after)
        if after.get("documentType") == "contractSignature":
            self.set_author_of_object(after)
            self.validate_object_author(before, after)
            self.validate_contract_signature_duplicate(after)

    def validate_contract_signature_duplicate(self, doc_data):
        contract_docs = deepcopy(self.request.validated["contract"].get("documents", []))
        new_documents = self.request.validated["data"]
        if isinstance(new_documents, list):  # POST (array of docs)
            contract_docs.extend(new_documents)
        else:  # PATCH/PUT
            contract_docs.append(doc_data)
        for prev_doc in contract_docs:
            if (
                prev_doc.get("documentType") == "contractSignature"
                and prev_doc["author"] == doc_data["author"]
                and prev_doc["id"] != doc_data["id"]
            ):
                raise_operation_error(
                    self.request,
                    f"Contract signature for {doc_data['author']} already exists",
                    location="body",
                    name="documentType",
                )

    def validate_object_author(self, before, after):
        if before.get("author") and before["author"] != after["author"]:
            raise_operation_error(
                self.request,
                "Only author can update this object",
                location="url",
                name="role",
            )
