from uuid import uuid4

from schematics.exceptions import ValidationError
from schematics.types import MD5Type, StringType
from schematics.types.serializable import serializable

from openprocurement.api.context import get_request_now
from openprocurement.api.procedure.context import get_tender
from openprocurement.api.procedure.models.base import Model
from openprocurement.api.procedure.models.document import (
    ConfidentialDocumentMixin,
    ConfidentialityType,
    PostConfidentialDocumentMixin,
)
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
    "proposal",
    "extensionReport",
    "deviationReport",
)


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


def validate_relatedItem(related_item, document_of):
    if not related_item and document_of in ("item", "lot"):
        raise ValidationError("This field is required.")

    tender = get_tender()
    if document_of == "lot" and not any(i and related_item == i["id"] for i in tender.get("lots", "")):
        raise ValidationError("relatedItem should be one of lots")
    if document_of == "item" and not any(i and related_item == i["id"] for i in tender.get("items", "")):
        raise ValidationError("relatedItem should be one of items")


def validate_tender_document_relations(data, documents):
    if documents:
        lot_ids = {lot["id"] for lot in data.get("lots") or ""}
        item_ids = {i["id"] for i in data.get("items") or ""}
        for d in documents:
            related_type = d.get("documentOf")
            related_item = d.get("relatedItem")
            if related_type == "lot":
                if related_item not in lot_ids:
                    raise ValidationError([{"relatedItem": ["relatedItem should be one of lots"]}])
            elif related_type == "item":
                if related_item not in item_ids:
                    raise ValidationError([{"relatedItem": ["relatedItem should be one of items"]}])


class BasePostDocument(BaseDocument):
    hash = HashType()
    title = StringType(required=True)  # A title of the document.
    format = StringType(required=True, regex=r"^[-\w]+/[-\.\w\+]+$")
    url = StringType(required=True)  # Link to the document or attachment.
    documentOf = StringType(required=True, choices=["tender", "item", "lot"], default="tender")
    language = StringType(required=True, choices=["uk", "en", "ru"], default="uk")

    def validate_relatedItem(self, data, related_item):
        validate_relatedItem(related_item, data.get("documentOf"))


class PostDocument(BasePostDocument, PostConfidentialDocumentMixin):
    # "create": blacklist("id", "datePublished", "dateModified", "author", "download_url"),

    @serializable
    def datePublished(self):
        return get_request_now().isoformat()

    @serializable
    def dateModified(self):
        return get_request_now().isoformat()

    id = MD5Type(required=True, default=lambda: uuid4().hex)


class PostComplaintDocument(PostDocument):
    documentOf = StringType(required=True, choices=["tender", "item", "lot", "post"], default="tender")


class Document(BaseDocument, ConfidentialDocumentMixin):
    # "create": blacklist("id", "datePublished", "dateModified", "author", "download_url"),
    id = MD5Type(required=True)
    datePublished = StringType(required=True)
    hash = HashType()
    title = StringType(required=True)  # A title of the document.
    format = StringType(required=True, regex=r"^[-\w]+/[-\.\w\+]+$")
    url = StringType(required=True)  # Link to the document or attachment.
    documentOf = StringType(required=True, choices=["tender", "item", "lot", "post"])
    dateModified = StringType()
    author = StringType()
    language = StringType(choices=["uk", "en", "ru"])

    def validate_relatedItem(self, data, related_item):
        validate_relatedItem(related_item, data.get("documentOf"))


class PatchDocument(BaseDocument):
    # "edit": blacklist("id", "url", "datePublished", "dateModified", "author", "hash", "download_url"),
    documentOf = StringType(choices=["tender", "item", "lot"])
    language = StringType(choices=["uk", "en", "ru"])
    confidentiality = StringType(
        choices=[
            ConfidentialityType.PUBLIC.value,
            ConfidentialityType.BUYER_ONLY.value,
        ]
    )
    confidentialityRationale = StringType()

    @serializable
    def dateModified(self):
        return get_request_now().isoformat()


class PatchComplaintDocument(PatchDocument):
    documentOf = StringType(choices=["tender", "item", "lot", "post"])
