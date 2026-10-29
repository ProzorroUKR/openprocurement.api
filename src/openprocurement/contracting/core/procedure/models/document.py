from uuid import uuid4

from schematics.types import MD5Type, StringType
from schematics.types.serializable import serializable

from openprocurement.api.context import get_request_now
from openprocurement.api.procedure.models.document import (
    ConfidentialDocumentMixin,
    ConfidentialityType,
    PostConfidentialDocumentMixin,
)
from openprocurement.api.procedure.types import HashType
from openprocurement.tender.core.procedure.models.document import BaseDocument as BaseTenderDocument

DOCUMENT_OFS = (
    "tender",
    "item",
    "lot",
    "contract",
    "change",
)


# --- Base models ---


class BaseContractDocument(BaseTenderDocument):
    documentOf = StringType(choices=DOCUMENT_OFS)


class BaseTransactionDocument(BaseTenderDocument):
    documentOf = StringType(default="contract")


# --- Contract document models ---


class BasePostDocument(BaseContractDocument):
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
    title = StringType(required=True)
    format = StringType(required=True, regex=r"^[-\w]+/[-\.\w\+]+$")
    url = StringType(required=True)
    documentOf = StringType(choices=DOCUMENT_OFS, default="contract")
    author = StringType()


class BasePatchDocument(BaseContractDocument):
    documentOf = StringType(choices=DOCUMENT_OFS)

    @serializable
    def dateModified(self):
        return get_request_now().isoformat()


class BaseDocument(BaseContractDocument):
    id = MD5Type(required=True)
    hash = HashType()
    title = StringType(required=True)  # A title of the document.
    format = StringType(required=True, regex=r"^[-\w]+/[-\.\w\+]+$")
    url = StringType(required=True)  # Link to the document or attachment.
    documentOf = StringType(choices=DOCUMENT_OFS, default="contract")
    datePublished = StringType(required=True)
    dateModified = StringType()
    author = StringType()


# --- Transaction document models ---


class PostTransactionDocument(BaseTransactionDocument, BasePostDocument):
    pass


class TransactionDocument(BaseTransactionDocument, BaseDocument):
    pass


class PostDocument(BasePostDocument, PostConfidentialDocumentMixin):
    pass


class PatchDocument(BasePatchDocument):
    confidentiality = StringType(
        choices=[
            ConfidentialityType.PUBLIC.value,
            ConfidentialityType.BUYER_ONLY.value,
        ]
    )
    confidentialityRationale = StringType()


class Document(BaseDocument, ConfidentialDocumentMixin):
    pass
