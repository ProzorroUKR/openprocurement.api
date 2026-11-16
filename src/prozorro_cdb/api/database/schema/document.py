from datetime import datetime
from enum import StrEnum
from uuid import uuid4

from pydantic import Field

from prozorro_cdb.api.database.schema.common import BaseModel


class DocumentTypes(StrEnum):
    tenderNotice = "tenderNotice"
    awardNotice = "awardNotice"
    contractNotice = "contractNotice"
    notice = "notice"
    biddingDocuments = "biddingDocuments"
    technicalSpecifications = "technicalSpecifications"
    evaluationCriteria = "evaluationCriteria"
    clarifications = "clarifications"
    shortlistedFirms = "shortlistedFirms"
    riskProvisions = "riskProvisions"
    billOfQuantity = "billOfQuantity"
    bidders = "bidders"
    conflictOfInterest = "conflictOfInterest"
    debarments = "debarments"
    evaluationReports = "evaluationReports"
    winningBid = "winningBid"
    complaints = "complaints"
    contractSigned = "contractSigned"
    contractArrangements = "contractArrangements"
    contractSchedule = "contractSchedule"
    contractAnnexe = "contractAnnexe"
    contractGuarantees = "contractGuarantees"
    subContract = "subContract"
    eligibilityCriteria = "eligibilityCriteria"
    contractProforma = "contractProforma"
    commercialProposal = "commercialProposal"
    qualificationDocuments = "qualificationDocuments"
    eligibilityDocuments = "eligibilityDocuments"
    registerExtract = "registerExtract"
    registerUSR = "registerUSR"
    registerFiscal = "registerFiscal"
    evidence = "evidence"
    register = "register"
    contractSignature = "contractSignature"
    violationReportSignature = "violationReportSignature"
    violationReportEvidence = "violationReportEvidence"
    acceptanceReport = "acceptanceReport"


class DocumentLanguage(StrEnum):
    UK = "uk"
    EN = "en"
    RU = "ru"


class Document(BaseModel):
    id: str = Field(default_factory=lambda: uuid4().hex)
    hash: str
    url: str
    dateModified: datetime
    datePublished: datetime

    documentType: DocumentTypes | None = None
    title: str | None = None
    title_en: str | None = None
    title_ru: str | None = None
    description: str | None = None
    description_en: str | None = None
    description_ru: str | None = None
    format: str | None = Field(None, pattern=r"^[-\w]+/[-\.\w\+]+$")
    language: DocumentLanguage | None = DocumentLanguage.UK
    relatedItem: str | None = None  # MD5Type → str з regex
