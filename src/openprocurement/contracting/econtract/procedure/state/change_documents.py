from copy import deepcopy

from openprocurement.api.utils import raise_operation_error
from openprocurement.contracting.core.procedure.state.document import (
    ContractDocumentState as BaseContractDocumentState,
)


class EContractChangeDocumentState(BaseContractDocumentState):
    def validate_document_post(self, data):
        if data.get("documentType") == "contractSignature":
            self.set_author_of_object(data)
            self.validate_change_signature_duplicate(data)

    def document_on_post(self, data):
        super().document_on_post(data)
        self.activate_change_if_signed(data)

    def activate_change_if_signed(self, doc):
        contract = self.request.validated["contract"]
        change = self.request.validated["change"]

        docs = deepcopy(change.get("documents", []))
        docs.append(doc)

        suppliers_count = len(contract.get("suppliers", []))
        participants_count = suppliers_count + 1  # all suppliers + buyer signature
        signs_count = len([doc for doc in docs if doc.get("documentType") == "contractSignature"])
        if signs_count == participants_count:
            self.set_object_status(change, "active")

    def validate_document_patch(self, before, after):
        if after.get("documentType") == "contractSignature":
            self.set_author_of_object(after)
            self.validate_object_author(before, after)
            self.validate_contract_signature_duplicate(after)

    def validate_change_signature_duplicate(self, doc_data):
        change_docs = deepcopy(self.request.validated["change"].get("documents", []))
        new_documents = self.request.validated["data"]
        if isinstance(new_documents, list):  # POST (array of docs)
            change_docs.extend(new_documents)
        else:  # PATCH/PUT
            change_docs.append(doc_data)
        for prev_doc in change_docs:
            if (
                prev_doc.get("documentType") == "contractSignature"
                and prev_doc["author"] == doc_data["author"]
                and prev_doc["id"] != doc_data["id"]
            ):
                raise_operation_error(
                    self.request,
                    f"Contract change signature for {doc_data['author']} already exists",
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
