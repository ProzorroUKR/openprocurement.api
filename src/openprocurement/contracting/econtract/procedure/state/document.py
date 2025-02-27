from openprocurement.api.constants_env import (
    CONFIDENTIAL_EDRPOU_LIST,
    CONTRACT_CONFIDENTIAL_DOCS_FROM,
)
from openprocurement.api.procedure.context import get_tender
from openprocurement.api.procedure.models.document import ConfidentialityTypes
from openprocurement.api.utils import raise_operation_error
from openprocurement.contracting.core.procedure.utils import is_contract_owner
from openprocurement.contracting.econtract.procedure.state.contract import (
    EContractState,
)
from openprocurement.tender.cfaselectionua.constants import CFA_SELECTION
from openprocurement.tender.core.procedure.state.document import BaseDocumentStateMixing
from openprocurement.tender.core.procedure.utils import tender_created_before

CONFIDENTIAL_DOCS_CAUSES = (
    "criticalInfrastructure",
    "civilProtection",
    "RNBO",
    "naturalGas",
    "UZ",
    "defencePurchase",
)


class EContractDocumentState(BaseDocumentStateMixing, EContractState):
    def validate_document_post(self, data):
        tender = self.request.validated["tender"]
        award = self.request.validated["award"]
        self.validate_cancellation_blocks(self.request, tender, lot_id=award.get("lotID"))

    def document_on_post(self, data):
        super().document_on_post(data)
        self.validate_confidentiality(data)

    def validate_confidentiality(self, data):
        if tender_created_before(CONTRACT_CONFIDENTIAL_DOCS_FROM):
            return
        tender = get_tender()
        if (
            data.get("documentOf") in ("contract", "change")
            and data.get("documentType") in ("contractSigned", "contractAnnexe")
            and tender.get("cause") in CONFIDENTIAL_DOCS_CAUSES
        ) or (
            data.get("title") == "sign.p7s"
            and data.get("format") == "application/pkcs7-signature"
            and is_contract_owner(self.request, self.request.validated["contract"])
            and tender.get("procurementMethodType") != CFA_SELECTION  # in cfa all docs should be public
            and tender.get("procuringEntity", {}).get("identifier", {}).get("id") in CONFIDENTIAL_EDRPOU_LIST
        ):
            if data["confidentiality"] != ConfidentialityTypes.BUYER_ONLY:
                raise_operation_error(
                    self.request,
                    "Document should be confidential",
                    name="confidentiality",
                    status=422,
                )
        elif data["confidentiality"] == ConfidentialityTypes.BUYER_ONLY:
            raise_operation_error(
                self.request,
                "Document should be public",
                name="confidentiality",
                status=422,
            )

    def validate_document_patch(self, before, after):
        tender = self.request.validated["tender"]
        award = self.request.validated["award"]
        self.validate_cancellation_blocks(self.request, tender, lot_id=award.get("lotID"))

    def document_on_patch(self, before, after):
        super().document_on_patch(before, after)
        self.validate_confidentiality(after)
