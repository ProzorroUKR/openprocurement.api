from uuid import uuid4

from schematics.exceptions import ValidationError
from schematics.types import MD5Type, StringType
from schematics.types.serializable import serializable

from openprocurement.api.context import get_request_now
from openprocurement.api.procedure.context import get_contract, get_tender
from openprocurement.api.procedure.models.document import (
    ConfidentialDocumentMixin,
    ConfidentialityType,
)
from openprocurement.api.procedure.types import HashType
from openprocurement.tender.core.procedure.models.document import (
    BaseDocument as BaseTenderDocument,
)

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

    def validate_relatedItem(self, data, related_item):
        pass


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

    def validate_relatedItem(self, data, related_item):
        validate_relatedItem(related_item, data.get("documentOf"))


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

    def validate_relatedItem(self, data, related_item):
        validate_relatedItem(related_item, data.get("documentOf"))


# --- Transaction document models ---


class PostTransactionDocument(BaseTransactionDocument, BasePostDocument):
    pass


class TransactionDocument(BaseTransactionDocument, BaseDocument):
    pass


class PostDocument(BasePostDocument, ConfidentialDocumentMixin):
    def validate_relatedItem(self, data, related_item):
        validate_relatedItem(related_item, data.get("documentOf"))


class PatchDocument(BasePatchDocument):
    confidentiality = StringType(
        choices=[
            ConfidentialityType.PUBLIC.value,
            ConfidentialityType.BUYER_ONLY.value,
        ]
    )
    confidentialityRationale = StringType()


class Document(BaseDocument, ConfidentialDocumentMixin):
    def validate_relatedItem(self, data, related_item):
        validate_relatedItem(related_item, data.get("documentOf"))


# --- Validations ---


def is_obj_exist(parent_obj: dict, obj_id: str, container: str) -> bool:
    return any(i and obj_id == i["id"] for i in parent_obj.get(container, ""))


def validate_relatedItem(related_item: str, document_of: str) -> None:
    if document_of not in ["item", "change", "lot"]:
        return

    if not related_item:
        raise ValidationError("This field is required.")

    if document_of == "lot":
        parent_obj = get_tender()
    else:
        parent_obj = get_contract()

    if not parent_obj:
        return

    container = document_of + "s"

    if not is_obj_exist(parent_obj, related_item, container):
        raise ValidationError(f"relatedItem should be one of {container}")
