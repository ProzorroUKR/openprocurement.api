from enum import StrEnum
from uuid import uuid4

from pydantic import Field, computed_field, model_validator

from openprocurement.api.context import get_request_now
from openprocurement.api.procedure.errors import FieldError
from openprocurement.api.procedure.models.base import Model
from openprocurement.api.procedure.types import MD5, Hash


class DocumentType(StrEnum):
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
    CANCELLATION_REPORT = "cancellationReport"
    ACCEPTANCE_REPORT = "acceptanceReport"


class TenderDocumentType(StrEnum):
    """document types of tenders, contracts and plans"""

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
    PROGRESS_REPORT = "progressReport"
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
    PROPOSAL = "proposal"
    EXTENSION_REPORT = "extensionReport"
    DEVIATION_REPORT = "deviationReport"
    CANCELLATION_REPORT = "cancellationReport"
    ACCEPTANCE_REPORT = "acceptanceReport"


DOCUMENT_FORMAT_REGEX = r"^[-\w]+/[-\.\w\+]+$"


class DocumentLanguage(StrEnum):
    UK = "uk"
    EN = "en"
    RU = "ru"


class ConfidentialityType(StrEnum):
    PUBLIC = "public"
    BUYER_ONLY = "buyerOnly"


class BaseDocument(Model):
    documentType: DocumentType | None = None
    title: str | None = None  # A title of the document.
    title_en: str | None = None
    title_ru: str | None = None
    description: str | None = None  # A description of the document.
    description_en: str | None = None
    description_ru: str | None = None
    format: str | None = Field(None, pattern=DOCUMENT_FORMAT_REGEX)
    language: str | None = None
    relatedItem: MD5 | None = None


class PostDocument(BaseDocument):
    @computed_field
    def id(self) -> str:
        return uuid4().hex

    @computed_field
    def datePublished(self) -> str:
        return get_request_now().isoformat()

    @computed_field
    def dateModified(self) -> str:
        return get_request_now().isoformat()

    hash: Hash | None = None
    title: str  # A title of the document.
    format: str = Field(pattern=DOCUMENT_FORMAT_REGEX)
    url: str  # Link to the document or attachment.
    language: DocumentLanguage = "uk"


class Document(BaseDocument):
    id: MD5
    datePublished: str
    hash: Hash | None = None
    title: str  # A title of the document.
    format: str = Field(pattern=DOCUMENT_FORMAT_REGEX)
    url: str  # Link to the document or attachment.
    dateModified: str | None = None
    author: str | None = None
    language: DocumentLanguage = "uk"


class PatchDocument(BaseDocument):
    language: DocumentLanguage | None = None

    @computed_field
    def dateModified(self) -> str:
        return get_request_now().isoformat()


def validate_confidentiality_rationale(confidentiality: str | None, rationale: str | None) -> None:
    if confidentiality == ConfidentialityType.BUYER_ONLY:
        if not rationale:
            raise ValueError("confidentialityRationale is required")
        elif len(rationale) < 30:
            raise ValueError("confidentialityRationale should contain at least 30 characters")


class ConfidentialDocumentMixin(Model):
    confidentiality: ConfidentialityType | None = None
    confidentialityRationale: str | None = None

    @model_validator(mode="after")
    def validate_confidentiality_rationale(self):
        try:
            validate_confidentiality_rationale(self.confidentiality, self.confidentialityRationale)
        except ValueError as e:
            raise FieldError("confidentialityRationale", str(e))
        return self


class PostConfidentialDocumentMixin(ConfidentialDocumentMixin):
    confidentiality: ConfidentialityType = ConfidentialityType.PUBLIC.value


class BaseTenderDocument(Model):
    """`BaseDocument` with the document types of tenders, contracts and plans"""

    documentType: TenderDocumentType | None = None
    title: str | None = None  # A title of the document.
    title_en: str | None = None
    title_ru: str | None = None
    description: str | None = None  # A description of the document.
    description_en: str | None = None
    description_ru: str | None = None
    format: str | None = Field(None, pattern=DOCUMENT_FORMAT_REGEX)
    language: str | None = None
    relatedItem: MD5 | None = None
