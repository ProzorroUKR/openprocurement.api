# -*- coding: utf-8 -*-
from openprocurement.api.models import Model, HashType
from openprocurement.tender.core.procedure.context import get_tender, get_document, get_now
from uuid import uuid4
from schematics.exceptions import ValidationError
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
    documentOf = StringType(choices=["tender", "item", "lot"])
    relatedItem = MD5Type()


def validate_relatedItem(related_item, document_of):
    if not related_item and document_of in ("item", "lot"):
        raise ValidationError("This field is required.")

    tender = get_tender()
    if document_of == "lot" and not any(i and related_item == i["id"] for i in tender.get("lots", "")):
        raise ValidationError("relatedItem should be one of lots")
    if document_of == "item" and not any(i and related_item == i["id"] for i in tender.get("items", "")):
        raise ValidationError("relatedItem should be one of items")


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
    documentOf = StringType(required=True, choices=["tender", "item", "lot"], default="tender")

    def validate_relatedItem(self, data, related_item):
        validate_relatedItem(related_item, data.get("documentOf"))


class Document(BaseDocument):
    # "create": blacklist("id", "datePublished", "dateModified", "author", "download_url"),
    id = MD5Type(required=True)
    datePublished = StringType(required=True)
    hash = HashType()
    title = StringType(required=True)  # A title of the document.
    format = StringType(required=True, regex="^[-\w]+/[-\.\w\+]+$")
    url = StringType(required=True)  # Link to the document or attachment.
    documentOf = StringType(required=True, choices=["tender", "item", "lot"], default="tender")
    dateModified = StringType()
    author = StringType()

    def validate_relatedItem(self, data, related_item):
        validate_relatedItem(related_item, data.get("documentOf"))


class PatchDocument(BaseDocument):
    # "edit": blacklist("id", "url", "datePublished", "dateModified", "author", "hash", "download_url"),

    def validate_relatedItem(self, data, related_item):
        document_of = data.get("documentOf", get_document()["documentOf"])
        validate_relatedItem(related_item, document_of)

    @serializable
    def dateModified(self):
        return get_now().isoformat()
