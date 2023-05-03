from openprocurement.api.models import HashType
from openprocurement.api.context import get_now
from openprocurement.tender.core.procedure.models.document import BaseDocument
from uuid import uuid4
from schematics.types import StringType, MD5Type
from schematics.types.serializable import serializable


class ContractPostDocument(BaseDocument):
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


class ContractDocument(BaseDocument):
    id = MD5Type(required=True)
    datePublished = StringType(required=True)
    hash = HashType()
    title = StringType(required=True)  # A title of the document.
    format = StringType(required=True, regex="^[-\w]+/[-\.\w\+]+$")
    url = StringType(required=True)  # Link to the document or attachment.
    dateModified = StringType()
    author = StringType()


class ContractPatchDocument(BaseDocument):
    @serializable
    def dateModified(self):
        return get_now().isoformat()
