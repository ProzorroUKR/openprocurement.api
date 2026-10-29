from openprocurement.api.constants_env import (
    CONFIDENTIAL_EDRPOU_LIST,
    CONTRACT_CONFIDENTIAL_DOCS_FROM,
)
from openprocurement.api.procedure.context import get_tender
from openprocurement.api.procedure.models.document import ConfidentialityType
from openprocurement.api.utils import raise_operation_error
from openprocurement.api.validation import OPERATIONS
from openprocurement.contracting.core.procedure.models.document import Document, PatchDocument, PostDocument
from openprocurement.contracting.core.procedure.state.contract import ContractState
from openprocurement.contracting.core.procedure.utils import (
    get_tender_award_by_contract,
    is_confidential_document_allowed,
    is_contract_owner,
)
from openprocurement.tender.cfaselectionua.constants import CFA_SELECTION
from openprocurement.tender.core.procedure.state.document import BaseDocumentStateMixin
from openprocurement.tender.core.procedure.utils import tender_created_before

CONFIDENTIAL_DOCS_CAUSES = (
    "criticalInfrastructure",
    "civilProtection",
    "RNBO",
    "naturalGas",
    "UZ",
    "defencePurchase",
    "stateDebtServices",
    "energyCrisisRecovery",
    "criticalInfrastructure0109",
    "energyCrisisRecovery0109",
    "criticalInfrastructureLifeSupportProtection",
    "restorationOfEnergyFacilities",
    # negotiation
    "defenseNeeds",
)

CONFIDENTIAL_DOCS_CAUSES_CONTRACT_ONLY = ("veteransSportsEventsServices",)


class ContractDocumentState(BaseDocumentStateMixin, ContractState):
    post_data_model = PostDocument
    patch_data_model = PatchDocument
    data_model = Document

    document_post_owner_exempt_roles: tuple = ("admins",)
    document_update_owner_exempt_roles: tuple = ("admins",)
    # buyerOnly documents are downloaded only by the contract owner (and sas)
    document_download_confidentiality_check = True
    # relatedItem of the item / change / lot documents is an object of the contract / tender
    document_related_item_check = True

    # --- request validation (called from the views) ---

    def validate_document_post_request(self):
        self.validate_document_owner(self.document_post_owner_exempt_roles)
        self.validate_input_data(self.get_post_data_model(), allow_bulk=True)
        self.validate_documents_related_item()
        self.validate_document_operation_allowed()

    def validate_document_put_request(self):
        self.validate_document_owner(self.document_update_owner_exempt_roles)
        self.validate_input_data(self.get_post_data_model())
        self.update_doc_fields_on_put_document()
        self.validate_upload_document()
        self.validate_data_model(self.get_data_model())
        self.validate_documents_related_item()
        self.validate_document_operation_allowed()

    def validate_document_patch_request(self):
        self.validate_document_owner(self.document_update_owner_exempt_roles)
        self.validate_patch_input_data(self.get_patch_data_model())
        self.validate_patch_data(self.get_data_model(), "document")
        self.validate_documents_related_item()
        self.validate_document_operation_allowed()
        self.validate_document_related_change_pending()

    def validate_documents_related_item(self):
        if not self.document_related_item_check:
            return
        data = self.request.validated["data"]
        for document in data if isinstance(data, list) else [data]:
            document_of = document.get("documentOf")
            if document_of not in ("item", "change", "lot"):
                continue
            related_item = document.get("relatedItem")
            if not related_item:
                raise_operation_error(self.request, ["This field is required."], status=422, name="relatedItem")
            parent = self.request.validated["tender"] if document_of == "lot" else self.request.validated["contract"]
            container = f"{document_of}s"
            if not any(i and i["id"] == related_item for i in parent.get(container, "")):
                raise_operation_error(
                    self.request,
                    [f"relatedItem should be one of {container}"],
                    status=422,
                    name="relatedItem",
                )

    def validate_document_owner(self, exempt_roles):
        if self.request.authenticated_role not in exempt_roles:
            self.validate_contract_owner()

    def validate_document_operation_allowed(self):
        status = self.request.validated["contract"]["status"]
        if status not in ("pending", "active"):
            raise_operation_error(
                self.request,
                f"Can't {OPERATIONS.get(self.request.method)} document in current ({status}) contract status",
            )

    def validate_document_related_change_pending(self):
        data = self.request.validated["data"]
        if "relatedItem" in data and data.get("documentOf") == "change":
            changes = self.request.validated["contract"].get("changes", "")
            if not any(c["id"] == data["relatedItem"] and c["status"] == "pending" for c in changes):
                raise_operation_error(self.request, "Can't add document to 'active' change")

    def validate_document_download_allowed(self):
        if not self.document_download_confidentiality_check:
            return
        if not self.request.params.get("download") or "document" not in self.request.validated:
            return
        if not is_confidential_document_allowed(self.request, self.request.validated["document"]):
            raise_operation_error(self.request, "Document download forbidden.")

    def validate_document_post(self, data):
        tender = self.request.validated["tender"]
        contract = self.request.validated["contract"]
        award = get_tender_award_by_contract(tender, contract)
        self.validate_cancellation_blocks(self.request, tender, lot_id=award.get("lotID"))

    def validate_confidentiality(self, data):
        if tender_created_before(CONTRACT_CONFIDENTIAL_DOCS_FROM):
            return
        tender = get_tender()
        cause = tender.get("cause") or tender.get("causeDetails", {}).get("code")
        contract_cause = cause in CONFIDENTIAL_DOCS_CAUSES_CONTRACT_ONLY
        contract_and_change_cause = cause in CONFIDENTIAL_DOCS_CAUSES
        document_ofs = ("contract",) if contract_cause else ("contract", "change")
        if (
            data.get("documentOf") in document_ofs
            and data.get("documentType") in ("contractSigned", "contractAnnexe")
            and (contract_cause or contract_and_change_cause)
        ) or (
            data.get("title") == "sign.p7s"
            and data.get("format") == "application/pkcs7-signature"
            and is_contract_owner(self.request, self.request.validated["contract"])
            and tender.get("procurementMethodType") != CFA_SELECTION  # in cfa all docs should be public
            and tender.get("procuringEntity", {}).get("identifier", {}).get("id") in CONFIDENTIAL_EDRPOU_LIST
        ):
            if data["confidentiality"] != ConfidentialityType.BUYER_ONLY:
                raise_operation_error(
                    self.request,
                    "Document should be confidential",
                    name="confidentiality",
                    status=422,
                )
        elif data["confidentiality"] == ConfidentialityType.BUYER_ONLY:
            raise_operation_error(
                self.request,
                "Document should be public",
                name="confidentiality",
                status=422,
            )

    def validate_document_patch(self, before, after):
        tender = self.request.validated["tender"]
        contract = self.request.validated["contract"]
        award = get_tender_award_by_contract(tender, contract)
        self.validate_cancellation_blocks(self.request, tender, lot_id=award.get("lotID"))

    def document_always(self, data):
        self.validate_confidentiality(data)
