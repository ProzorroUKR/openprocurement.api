from enum import StrEnum
from typing import Literal

from openprocurement.api.procedure.models.document import BaseTenderDocument
from openprocurement.contracting.core.procedure.models.document import (
    Document as BaseDocument,
)
from openprocurement.contracting.core.procedure.models.document import (
    PatchDocument as BasePatchDocument,
)
from openprocurement.contracting.core.procedure.models.document import (
    PostDocument as BasePostDocument,
)


class ContractDocumentType(StrEnum):
    TENDER_NOTICE = "tenderNotice"
    AWARD_NOTICE = "awardNotice"
    CONTRACT_NOTICE = "contractNotice"
    NOTICE = "notice"
    BIDDING_DOCUMENTS = "biddingDocuments"
    TECHNICAL_SPECIFICATIONS = "technicalSpecifications"
    EVALUATION_CRITERIA = "evaluationCriteria"
    CLARIFICATIONS = "clarifications"
    SHORTLISTED_FIRMS = "shortlistedFirms"
    RISK_PROVISIONS = "riskProvisions"
    BILL_OF_QUANTITY = "billOfQuantity"
    BIDDERS = "bidders"
    CONFLICT_OF_INTEREST = "conflictOfInterest"
    DEBARMENTS = "debarments"
    EVALUATION_REPORTS = "evaluationReports"
    WINNING_BID = "winningBid"
    COMPLAINTS = "complaints"
    CONTRACT_SIGNED = "contractSigned"
    CONTRACT_ARRANGEMENTS = "contractArrangements"
    CONTRACT_SCHEDULE = "contractSchedule"
    CONTRACT_ANNEXE = "contractAnnexe"
    CONTRACT_GUARANTEES = "contractGuarantees"
    SUB_CONTRACT = "subContract"
    ELIGIBILITY_CRITERIA = "eligibilityCriteria"
    CONTRACT_PROFORMA = "contractProforma"
    COMMERCIAL_PROPOSAL = "commercialProposal"
    QUALIFICATION_DOCUMENTS = "qualificationDocuments"
    ELIGIBILITY_DOCUMENTS = "eligibilityDocuments"
    REGISTER_EXTRACT = "registerExtract"
    REGISTER_USR = "registerUSR"
    REGISTER_FISCAL = "registerFiscal"
    EVIDENCE = "evidence"
    REGISTER = "register"
    CONTRACT_SIGNATURE = "contractSignature"
    PROGRESS_REPORT = "progressReport"
    TERMINATION_REPORT = "terminationReport"


class PostDocument(BasePostDocument):
    documentType: ContractDocumentType | None = None


class PatchDocument(BasePatchDocument):
    documentType: ContractDocumentType | None = None


class Document(BaseDocument):
    documentType: ContractDocumentType | None = None
    author: str | None = None


class PostTerminationDetailsDocument(PostDocument):
    documentType: Literal["terminationReport"]


class BaseChangeDocument(BaseTenderDocument):
    documentOf: str = "change"
    documentType: ContractDocumentType | None = None


class PostChangeDocument(BaseChangeDocument, PostDocument):
    pass


class ChangeDocument(BaseChangeDocument, Document):
    pass
