from copy import deepcopy

from openprocurement.api.constants_env import SIGNATURE_VERIFICATION_ENABLED
from openprocurement.api.context import get_request_now
from openprocurement.api.procedure.serializers.document import load_document_content
from openprocurement.api.procedure.validation import (
    validate_apisign_signature_cert,
    validate_apisign_signature_type,
)
from openprocurement.api.utils import raise_operation_error, verify_signature_apisign
from openprocurement.contracting.core.procedure.state.document import (
    ContractDocumentState as BaseContractDocumentState,
)


class EContractChangeDocumentState(BaseContractDocumentState):
    def validate_document_post(self, data):
        if data.get("documentType") == "contractSignature":
            self.set_author_of_object(data)
            self.validate_change_signature_duplicate(data)
            self.validate_contract_change_signature(data)
        else:
            raise_operation_error(
                self.request,
                "Only contractSignature documentType is allowed",
            )

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
            change["dateSigned"] = get_request_now().isoformat()
            self.set_object_status(change, "active")

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

    def validate_contract_change_signature(self, doc_data):
        if not SIGNATURE_VERIFICATION_ENABLED:
            return
        # Get signature file from ds
        signature = load_document_content(doc_data)
        # Find contract notice document
        pdf_doc = None
        change = self.request.validated["change"]
        for doc in change.get("documents", []):
            if doc.get("documentType") == "contractNotice":
                pdf_doc = doc
                break
        if not pdf_doc:
            raise_operation_error(
                self.request,
                "Contract change pdf not found",
                location="body",
                name="documents",
            )
        # Get pdf file from ds
        pdf = load_document_content(doc)
        # Verify signature
        verify_data = verify_signature_apisign(pdf, signature)
        # Validate signature
        validate_apisign_signature_type(verify_data)
        validate_apisign_signature_cert(verify_data)
