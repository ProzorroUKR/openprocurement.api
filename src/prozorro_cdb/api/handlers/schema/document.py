from pydantic import Field, HttpUrl

from prozorro_cdb.api.database.schema.document import (
    Document,
    DocumentLanguage,
    DocumentTypes,
)
from prozorro_cdb.api.handlers.schema.common import BaseRequestModel


class BaseDocument(BaseRequestModel):
    title: str | None = None
    title_en: str | None = None
    title_ru: str | None = None
    description: str | None = None
    description_en: str | None = None
    description_ru: str | None = None
    language: DocumentLanguage | None = DocumentLanguage.UK
    relatedItem: str | None = None  # MD5Type → str з regex


class PostDocument(BaseDocument):
    hash: str
    url: HttpUrl
    documentType: DocumentTypes | None = None
    format: str | None = Field(None, pattern=r"^[-\w]+/[-\.\w\+]+$")


class PatchDocument(BaseDocument):
    language: DocumentLanguage | None = None


class GetDocumentResponse(Document):
    previousVersions: list[Document]
