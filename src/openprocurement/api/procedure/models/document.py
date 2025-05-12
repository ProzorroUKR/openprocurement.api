from enum import StrEnum
from uuid import uuid4

from schematics.exceptions import ValidationError
from schematics.types import MD5Type, StringType
from schematics.types.serializable import serializable

from openprocurement.api.context import get_request_now
from openprocurement.api.procedure.models.base import Model
from openprocurement.api.procedure.types import HashType

DOCUMENT_TYPES = (
    "tenderNotice",
    "awardNotice",
    "contractNotice",
    "notice",
    "biddingDocuments",
    "technicalSpecifications",
    "evaluationCriteria",
    "clarifications",
    "shortlistedFirms",
    "riskProvisions",
    "billOfQuantity",
    "bidders",
    "conflictOfInterest",
    "debarments",
    "evaluationReports",
    "winningBid",
    "complaints",
    "contractSigned",
    "contractArrangements",
    "contractSchedule",
    "contractAnnexe",
    "contractGuarantees",
    "subContract",
    "eligibilityCriteria",
    "contractProforma",
    "commercialProposal",
    "qualificationDocuments",
    "eligibilityDocuments",
    "registerExtract",
    "registerFiscal",
    "winningBid",
    "evidence",
    "register",
)


class ConfidentialityType(StrEnum):
    BUYER_ONLY = "buyerOnly"
    PUBLIC = "public"


class BaseDocument(Model):
    documentType = StringType(choices=DOCUMENT_TYPES)
    title = StringType()  # A title of the document.
    title_en = StringType()
    title_ru = StringType()
    description = StringType()  # A description of the document.
    description_en = StringType()
    description_ru = StringType()
    format = StringType(regex=r"^[-\w]+/[-\.\w\+]+$")
    language = StringType()
    relatedItem = MD5Type()


class PostDocument(BaseDocument):
    @serializable
    def id(self):
        return uuid4().hex

    @serializable
    def datePublished(self):
        return get_request_now().isoformat()

    @serializable
    def dateModified(self):
        return get_request_now().isoformat()

    hash = HashType()
    title = StringType(required=True)  # A title of the document.
    format = StringType(required=True, regex=r"^[-\w]+/[-\.\w\+]+$")
    url = StringType(required=True)  # Link to the document or attachment.
    language = StringType(required=True, choices=["uk", "en", "ru"], default="uk")


class Document(BaseDocument):
    id = MD5Type(required=True)
    datePublished = StringType(required=True)
    hash = HashType()
    title = StringType(required=True)  # A title of the document.
    format = StringType(required=True, regex=r"^[-\w]+/[-\.\w\+]+$")
    url = StringType(required=True)  # Link to the document or attachment.
    dateModified = StringType()
    author = StringType()
    language = StringType(required=True, choices=["uk", "en", "ru"], default="uk")


class PatchDocument(BaseDocument):
    language = StringType(choices=["uk", "en", "ru"])

    @serializable
    def dateModified(self):
        return get_request_now().isoformat()


def validate_confidentiality_rationale(data, val):
    confidentiality = data.get("confidentiality")
    if confidentiality == ConfidentialityType.BUYER_ONLY:
        if not val:
            raise ValidationError("confidentialityRationale is required")
        elif len(val) < 30:
            raise ValidationError("confidentialityRationale should contain at least 30 characters")


class ConfidentialDocumentMixin(Model):
    confidentiality = StringType(
        choices=[
            ConfidentialityType.PUBLIC.value,
            ConfidentialityType.BUYER_ONLY.value,
        ],
        default=ConfidentialityType.PUBLIC.value,
    )
    confidentialityRationale = StringType()

    def validate_confidentialityRationale(self, data, val):
        validate_confidentiality_rationale(data, val)
