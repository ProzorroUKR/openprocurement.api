from datetime import datetime
from enum import StrEnum
from typing import Optional
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
    registerFiscal = "registerFiscal"
    evidence = "evidence"
    register = "register"
    contractSignature = "contractSignature"
    violationReportSignature = "violationReportSignature"
    violationReportEvidence = "violationReportEvidence"


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

    documentType: Optional[DocumentTypes] = None
    title: Optional[str] = None
    title_en: Optional[str] = None
    title_ru: Optional[str] = None
    description: Optional[str] = None
    description_en: Optional[str] = None
    description_ru: Optional[str] = None
    format: Optional[str] = Field(None, pattern=r"^[-\w]+/[-\.\w\+]+$")
    language: Optional[DocumentLanguage] = DocumentLanguage.UK
    relatedItem: Optional[str] = None  # MD5Type → str з regex
