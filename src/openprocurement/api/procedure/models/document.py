from openprocurement.api.models import Model, HashType
from openprocurement.api.context import get_now
from uuid import uuid4
from schematics.types import StringType, MD5Type
from schematics.types.serializable import serializable

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


class BaseDocument(Model):
    documentType = StringType(choices=DOCUMENT_TYPES)
    title = StringType()  # A title of the document.
    title_en = StringType()
    title_ru = StringType()
    description = StringType()  # A description of the document.
    description_en = StringType()
    description_ru = StringType()
    format = StringType(regex="^[-\w]+/[-\.\w\+]+$")
    language = StringType()
    relatedItem = MD5Type()


class PostDocument(BaseDocument):
    # "create": blacklist("id", "datePublished", "dateModified", "author", "download_url"),
    @serializable
    def id(self):
        return uuid4().hex

    @serializable
    def datePublished(self):
        return get_now().isoformat()

    @serializable
    def dateModified(self):
        return get_now().isoformat()

    hash = HashType()
    title = StringType(required=True)  # A title of the document.
    format = StringType(required=True, regex="^[-\w]+/[-\.\w\+]+$")
    url = StringType(required=True)  # Link to the document or attachment.
    language = StringType(required=True, choices=["uk", "en", "ru"], default="uk")


class Document(BaseDocument):
    # "create": blacklist("id", "datePublished", "dateModified", "author", "download_url"),
    id = MD5Type(required=True)
    datePublished = StringType(required=True)
    hash = HashType()
    title = StringType(required=True)  # A title of the document.
    format = StringType(required=True, regex="^[-\w]+/[-\.\w\+]+$")
    url = StringType(required=True)  # Link to the document or attachment.
    dateModified = StringType()
    author = StringType()
    language = StringType(required=True, choices=["uk", "en", "ru"], default="uk")


class PatchDocument(BaseDocument):
    # "edit": blacklist("id", "url", "datePublished", "dateModified", "author", "hash", "download_url"),
    language = StringType(choices=["uk", "en", "ru"])

    @serializable
    def dateModified(self):
        return get_now().isoformat()