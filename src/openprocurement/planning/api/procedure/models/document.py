from uuid import uuid4

from schematics.types import MD5Type, StringType
from schematics.types.serializable import serializable

from openprocurement.api.context import get_now
from openprocurement.api.procedure.types import HashType
from openprocurement.tender.core.procedure.models.document import (
    BaseDocument,
    BasePostDocument,
    validate_relatedItem,
)


class PostDocument(BasePostDocument):
    @serializable
    def datePublished(self):
        return get_now().isoformat()

    @serializable
    def dateModified(self):
        return get_now().isoformat()

    id = MD5Type(required=True, default=lambda: uuid4().hex)
    documentOf = StringType(required=False)


class PatchDocument(BaseDocument):
    language = StringType(choices=["uk", "en", "ru"])
    documentOf = StringType(required=False)

    @serializable
    def dateModified(self):
        return get_now().isoformat()


class Document(BaseDocument):
    id = MD5Type(required=True)
    datePublished = StringType(required=True)
    hash = HashType()
    title = StringType(required=True)  # A title of the document.
    format = StringType(required=True, regex=r"^[-\w]+/[-\.\w\+]+$")
    url = StringType(required=True)  # Link to the document or attachment.
    documentOf = StringType(required=False)
    dateModified = StringType()
    author = StringType()
    language = StringType(choices=["uk", "en", "ru"])

    def validate_relatedItem(self, data, related_item):
        validate_relatedItem(related_item, data.get("documentOf"))
