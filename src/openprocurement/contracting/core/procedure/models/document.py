from openprocurement.api.procedure.types import HashType
from openprocurement.api.procedure.context import get_contract
from openprocurement.api.context import get_now
from openprocurement.tender.core.procedure.models.document import BaseDocument
from uuid import uuid4
from schematics.exceptions import ValidationError
from schematics.types import StringType, MD5Type
from schematics.types.serializable import serializable


DOCUMENT_OFS = (
    "tender",
    "item",
    "lot",
    "contract",
    "change",
)


# --- Base models ---

class BaseContractDocument(BaseDocument):
    documentOf = StringType(choices=DOCUMENT_OFS)


class BaseTransactionDocument(BaseDocument):
    documentOf = StringType(default="contract")

    def validate_relatedItem(self, data, related_item):
        pass


# --- Contract document models ---

class PostDocument(BaseContractDocument):
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
    title = StringType(required=True)
    format = StringType(required=True, regex="^[-\w]+/[-\.\w\+]+$")
    url = StringType(required=True)
    documentOf = StringType(choices=DOCUMENT_OFS, default="contract")
    author = StringType()

    def validate_relatedItem(self, data, related_item):
        validate_relatedItem(related_item, data.get("documentOf"))


class PatchDocument(BaseContractDocument):
    documentOf = StringType(choices=DOCUMENT_OFS)
    @serializable
    def dateModified(self):
        return get_now().isoformat()


class Document(BaseContractDocument):
    id = MD5Type(required=True)
    hash = HashType()
    title = StringType(required=True)  # A title of the document.
    format = StringType(required=True, regex="^[-\w]+/[-\.\w\+]+$")
    url = StringType(required=True)  # Link to the document or attachment.
    documentOf = StringType(choices=DOCUMENT_OFS, default="contract")
    datePublished = StringType(required=True)
    dateModified = StringType()
    author = StringType()

    def validate_relatedItem(self, data, related_item):
        validate_relatedItem(related_item, data.get("documentOf"))


# --- Transaction document models ---


class PostTransactionDocument(BaseTransactionDocument, PostDocument):
    pass


class TransactionDocument(BaseTransactionDocument, Document):
    pass


# --- Validations ---
def validate_relatedItem(related_item: str, document_of: str) -> None:
    if not related_item and document_of in ["item", "change"]:
        raise ValidationError("This field is required.")

    contract = get_contract()
    if not contract:
        return

    if document_of == "change" and not any(i and related_item == i["id"] for i in contract.get("changes", "")):
        raise ValidationError("relatedItem should be one of changes")
    if document_of == "item" and not any(i and related_item == i["id"] for i in contract.get("items", "")):
        raise ValidationError("relatedItem should be one of items")


