from typing import Any, Literal
from uuid import uuid4

from pydantic import Field, computed_field

from openprocurement.api.context import get_request_now
from openprocurement.api.procedure.errors import ValidationError
from openprocurement.api.procedure.models.base import Model, model_field_validator
from openprocurement.api.procedure.models.document import (
    ConfidentialDocumentMixin,
    ConfidentialityType,
    PostConfidentialDocumentMixin,
    TenderDocumentType,
)
from openprocurement.api.procedure.types import (
    MD5,
    Hash,
)


class BaseDocument(Model):
    documentType: TenderDocumentType | None = None
    title: str | None = None
    title_en: str | None = None
    title_ru: str | None = None
    description: str | None = None
    description_en: str | None = None
    description_ru: str | None = None
    format: str | None = Field(None, pattern=r"^[-\w]+/[-\.\w\+]+$")
    language: str | None = None
    relatedItem: MD5 | None = None


def validate_related_item(related_item, document_of):
    # the tender items / lots of relatedItem are checked by the state (TenderState.validate_documents_related_item)
    if not related_item and document_of in ("item", "lot"):
        raise ValidationError("This field is required.")


def validate_tender_document_relations(tender, documents):
    if documents:
        lot_ids = {lot.id for lot in getattr(tender, "lots", None) or []}  # not fields of all the tenders
        item_ids = {i.id for i in getattr(tender, "items", None) or []}
        for d in documents:
            related_type = d.documentOf
            related_item = d.relatedItem
            if related_type == "lot":
                if related_item not in lot_ids:
                    raise ValidationError([{"relatedItem": ["relatedItem should be one of lots"]}])
            elif related_type == "item":
                if related_item not in item_ids:
                    raise ValidationError([{"relatedItem": ["relatedItem should be one of items"]}])


class BasePostDocument(BaseDocument):
    hash: Hash | None = None
    title: str
    format: str = Field(pattern=r"^[-\w]+/[-\.\w\+]+$")
    url: str
    documentOf: Literal["tender", "item", "lot"] = "tender"
    language: Literal["uk", "en", "ru"] = "uk"

    @model_field_validator("relatedItem")
    def validate_related_item(self, related_item):
        validate_related_item(related_item, self.documentOf)


class PostDocument(BasePostDocument, PostConfidentialDocumentMixin):
    @computed_field
    def datePublished(self) -> Any:
        return get_request_now().isoformat()

    @computed_field
    def dateModified(self) -> Any:
        return get_request_now().isoformat()

    id: MD5 = Field(default_factory=lambda: uuid4().hex)


class PostComplaintDocument(PostDocument):
    documentOf: Literal["tender", "item", "lot", "post"] = "tender"


class Document(BaseDocument, ConfidentialDocumentMixin):
    id: MD5
    datePublished: str
    hash: Hash | None = None
    title: str
    format: str = Field(pattern=r"^[-\w]+/[-\.\w\+]+$")
    url: str
    documentOf: Literal["tender", "item", "lot", "post"]
    dateModified: str | None = None
    author: str | None = None
    language: Literal["uk", "en", "ru"] | None = None

    @model_field_validator("relatedItem")
    def validate_related_item(self, related_item):
        validate_related_item(related_item, self.documentOf)


class PatchDocument(BaseDocument):
    documentOf: Literal["tender", "item", "lot"] | None = None
    language: Literal["uk", "en", "ru"] | None = None
    confidentiality: ConfidentialityType | None = None
    confidentialityRationale: str | None = None

    @computed_field
    def dateModified(self) -> Any:
        return get_request_now().isoformat()


class PatchComplaintDocument(PatchDocument):
    documentOf: Literal["tender", "item", "lot", "post"] | None = None
