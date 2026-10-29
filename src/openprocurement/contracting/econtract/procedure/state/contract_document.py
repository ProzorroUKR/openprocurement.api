from openprocurement.api.constants_env import SIGNATURE_VERIFICATION_ENABLED
from openprocurement.api.procedure.context import get_tender
from openprocurement.api.procedure.serializers.document import load_document_content
from openprocurement.api.procedure.validation import (
    validate_apisign_signature_cert,
    validate_apisign_signature_type,
)
from openprocurement.api.utils import raise_operation_error, verify_signature_apisign
from openprocurement.api.validation import OPERATIONS
from openprocurement.contracting.core.procedure.state.document import (
    ContractDocumentState,
)
from openprocurement.contracting.econtract.procedure.models.document import PostDocument
from openprocurement.tender.core.utils import tender_signature_verification_disabled


class EContractDocumentState(ContractDocumentState):
    post_data_model = PostDocument

    # --- request validation (called from the views) ---

    def validate_document_owner(self, exempt_roles):
        if self.request.authenticated_role not in exempt_roles:
            self.validate_contract_participant()

    def validate_document_operation_allowed(self):
        super().validate_document_operation_allowed()
        self.validate_document_signature_operation()

    def validate_document_signature_operation(self):
        """the contract is signed only while it is pending"""
        request = self.request
        status = request.validated["contract"]["status"]
        data = (
            request.validated["data"][0] if isinstance(request.validated["data"], list) else request.validated["data"]
        )
        # documentType of the request data or of the updated document
        document_type = data.get("documentType") or request.validated.get("document", {}).get("documentType")
        if document_type == "contractSignature" and status != "pending":
            raise_operation_error(
                request,
                f"Can't {OPERATIONS.get(request.method)} sign document in current ({status}) contract status",
            )

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
        if not SIGNATURE_VERIFICATION_ENABLED or tender_signature_verification_disabled(get_tender()):
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
