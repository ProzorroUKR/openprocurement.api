from openprocurement.api.constants_env import SIGNATURE_VERIFICATION_ENABLED
from openprocurement.api.procedure.serializers.document import load_document_content
from openprocurement.api.procedure.validation import (
    validate_apisign_signature_cert,
    validate_apisign_signature_type,
)
from openprocurement.api.utils import raise_operation_error, verify_signature_apisign
from openprocurement.contracting.core.procedure.state.document import (
    ContractDocumentState as BaseContractDocumentState,
)


class EContractDocumentState(BaseContractDocumentState):
    def validate_document_post(self, data):
        super().validate_document_post(data)
        if data.get("documentType") == "contractSignature":
            self.validate_contract_cancellations()
            self.set_author_of_object(data)
            self.validate_signatory_confirmed(data)
            self.validate_contract_signature(data)
        else:
            raise_operation_error(
                self.request,
                "Only contractSignature documentType is allowed",
            )

    def validate_contract_cancellations(self):
        contract = self.request.validated["contract"]
        if contract.get("cancellations", []):
            raise_operation_error(
                self.request,
                "Forbidden to sign contract with cancellation",
            )

    def validate_signatory_confirmed(self, doc_data):
        contract = self.request.validated["contract"]
        if doc_data["author"] in {x["role"] for x in contract.get("signatories", [])}:
            raise_operation_error(
                self.request,
                "Signatory was already confirmed.",
            )

    def validate_contract_signature(self, doc_data):
        if not SIGNATURE_VERIFICATION_ENABLED:
            return
        # Get signature file from ds
        signature = load_document_content(doc_data)
        # Find contract notice document
        pdf_doc = None
        contract = self.request.validated["contract"]
        for doc in contract.get("documents", []):
            if doc.get("documentType") == "contractNotice":
                pdf_doc = doc
                break
        if not pdf_doc:
            raise_operation_error(
                self.request,
                "Contract pdf not found",
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
