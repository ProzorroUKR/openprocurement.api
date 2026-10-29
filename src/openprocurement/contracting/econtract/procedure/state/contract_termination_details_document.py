from openprocurement.api.constants_env import SIGNATURE_VERIFICATION_ENABLED
from openprocurement.api.context import get_request_now
from openprocurement.api.procedure.context import get_tender
from openprocurement.api.procedure.serializers.document import load_document_content
from openprocurement.api.procedure.validation import (
    validate_apisign_signature_cert,
    validate_apisign_signature_type,
)
from openprocurement.api.utils import json_dumps, raise_operation_error, verify_signature_apisign
from openprocurement.contracting.core.procedure.models.access import AccessRole
from openprocurement.contracting.core.procedure.state.document import (
    ContractDocumentState,
)
from openprocurement.contracting.econtract.procedure.models.document import PostTerminationDetailsDocument
from openprocurement.contracting.econtract.procedure.serializers.termination_details import (
    ContractContextSerializer,
)
from openprocurement.contracting.econtract.procedure.state.contract import (
    EContractState,
)
from openprocurement.tender.core.utils import tender_signature_verification_disabled


class EContractTerminationDetailsDocumentState(ContractDocumentState):
    """
    Uploading a terminationSignature document is the only way terminationDetails
    moves draft -> active: the buyer signs the contract JSON as returned by
    ContractContextSerializer (the same data shown as `context.contract` on
    GET /termination_details?opt_context=true) offline with their own EDS
    tooling and uploads the resulting sign.p7s here. A successfully verified
    signature activates terminationDetails and terminates the contract as a
    side effect of this same request - there is no separate activation call.
    """

    post_data_model = PostTerminationDetailsDocument

    document_post_owner_exempt_roles: tuple = ("admins", "Administrator")
    document_download_confidentiality_check = False

    # --- request validation (called from the views) ---

    def validate_document_owner(self, exempt_roles):
        if self.request.authenticated_role not in exempt_roles:
            self.validate_contract_buyer()

    def validate_document_operation_allowed(self):
        if self.request.authenticated_role not in ("admins", "Administrator"):
            self.validate_contract_status_active()
        status = self.request.validated["termination_details"].get("status")
        if status != "draft":
            raise_operation_error(
                self.request,
                f"Can't add document to terminationDetails in current ({status}) status",
            )

    def validate_document_post(self, data):
        contract = self.request.validated["contract"]
        termination_details = self.request.validated["termination_details"]

        self.set_author_of_object(data)
        if data["author"] != AccessRole.BUYER.value:
            raise_operation_error(
                self.request,
                "terminationSignature document must be signed by buyer",
            )
        EContractState(self.request).validate_termination_details_requirements(contract, termination_details)
        self.validate_termination_signature(data)
        self.activate_termination_details(contract, termination_details)

    def validate_termination_signature(self, doc_data):
        if not SIGNATURE_VERIFICATION_ENABLED or tender_signature_verification_disabled(get_tender()):
            return
        contract = self.request.validated["contract"]
        content = json_dumps(ContractContextSerializer(contract).data, sort_keys=True).encode()
        signature = load_document_content(doc_data)
        verify_data = verify_signature_apisign(content, signature)
        validate_apisign_signature_type(verify_data)
        validate_apisign_signature_cert(verify_data)

    def activate_termination_details(self, contract: dict, termination_details: dict) -> None:
        termination_details["status"] = "active"
        termination_details["datePublished"] = get_request_now().isoformat()
        contract["status"] = "terminated"
