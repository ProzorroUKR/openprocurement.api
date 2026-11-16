from typing import Literal
from uuid import uuid4

from pydantic import Field, computed_field, model_validator

from openprocurement.api.context import get_request_now
from openprocurement.api.procedure.errors import REQUIRED_MESSAGE, FieldError
from openprocurement.api.procedure.models.document import BaseTenderDocument as BaseDocument
from openprocurement.api.procedure.types import MD5, Hash


class PostDocument(BaseDocument):
    hash: Hash | None = None
    title: str  # A title of the document.
    format: str = Field(pattern=r"^[-\w]+/[-\.\w\+]+$")
    url: str  # Link to the document or attachment.
    language: Literal["uk", "en", "ru"] = "uk"
    id: MD5 = Field(default_factory=lambda: uuid4().hex)
    documentOf: str | None = None

    @computed_field
    def datePublished(self) -> str:
        return get_request_now().isoformat()

    @computed_field
    def dateModified(self) -> str:
        return get_request_now().isoformat()

    @model_validator(mode="after")
    def validate_related_item(self):
        if not self.relatedItem and self.documentOf in ("item", "lot"):
            raise FieldError("relatedItem", REQUIRED_MESSAGE)
        return self


class PatchDocument(BaseDocument):
    language: Literal["uk", "en", "ru"] | None = None
    documentOf: str | None = None

    @computed_field
    def dateModified(self) -> str:
        return get_request_now().isoformat()


class Document(BaseDocument):
    id: MD5
    datePublished: str
    hash: Hash | None = None
    title: str  # A title of the document.
    format: str = Field(pattern=r"^[-\w]+/[-\.\w\+]+$")
    url: str  # Link to the document or attachment.
    documentOf: str | None = None
    dateModified: str | None = None
    author: str | None = None
    language: Literal["uk", "en", "ru"] | None = None
