from uuid import uuid4

from schematics.types import MD5Type, StringType
from schematics.types.serializable import serializable

from openprocurement.api.context import get_request_now
from openprocurement.api.procedure.types import HashType
from openprocurement.tender.core.procedure.models.document import BaseDocument


class ContractPostDocument(BaseDocument):
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


class ContractDocument(BaseDocument):
    id = MD5Type(required=True)
    datePublished = StringType(required=True)
    hash = HashType()
    title = StringType(required=True)  # A title of the document.
    format = StringType(required=True, regex=r"^[-\w]+/[-\.\w\+]+$")
    url = StringType(required=True)  # Link to the document or attachment.
    dateModified = StringType()
    author = StringType()


class ContractPatchDocument(BaseDocument):
    @serializable
    def dateModified(self):
        return get_request_now().isoformat()
