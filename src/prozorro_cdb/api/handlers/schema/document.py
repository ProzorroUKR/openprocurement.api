from typing import List, Optional

from pydantic import Field, HttpUrl

from prozorro_cdb.api.database.schema.document import (
    Document,
    DocumentLanguage,
    DocumentTypes,
)
from prozorro_cdb.api.handlers.schema.common import BaseRequestModel


class BaseDocument(BaseRequestModel):
    title: Optional[str] = None
    title_en: Optional[str] = None
    title_ru: Optional[str] = None
    description: Optional[str] = None
    description_en: Optional[str] = None
    description_ru: Optional[str] = None
    language: Optional[DocumentLanguage] = DocumentLanguage.UK
    relatedItem: Optional[str] = None  # MD5Type → str з regex


class PostDocument(BaseDocument):
    hash: str
    url: HttpUrl
    documentType: Optional[DocumentTypes] = None
    format: Optional[str] = Field(None, pattern=r"^[-\w]+/[-\.\w\+]+$")


class PatchDocument(BaseDocument):
    language: Optional[DocumentLanguage] = None


class GetDocumentResponse(Document):
    previousVersions: List[Document]
