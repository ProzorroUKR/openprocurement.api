from enum import StrEnum
from typing import Any
from uuid import uuid4

from pydantic import Field, computed_field

from openprocurement.api.context import get_request_now
from openprocurement.api.procedure.models.document import (
    BaseTenderDocument,
    ConfidentialDocumentMixin,
    ConfidentialityType,
    PostConfidentialDocumentMixin,
)
from openprocurement.api.procedure.types import (
    MD5,
    Hash,
)


class ContractDocumentOf(StrEnum):
    TENDER = "tender"
    ITEM = "item"
    LOT = "lot"
    CONTRACT = "contract"
    CHANGE = "change"


class BaseContractDocument(BaseTenderDocument):
    documentOf: ContractDocumentOf | None = None


class BaseTransactionDocument(BaseTenderDocument):
    documentOf: str = "contract"


class BasePostDocument(BaseContractDocument):
    @computed_field
    def id(self) -> Any:
        return uuid4().hex

    @computed_field
    def datePublished(self) -> Any:
        return get_request_now().isoformat()

    @computed_field
    def dateModified(self) -> Any:
        return get_request_now().isoformat()

    hash: Hash | None = None
    title: str
    format: str = Field(pattern=r"^[-\w]+/[-\.\w\+]+$")
    url: str
    documentOf: ContractDocumentOf = "contract"
    author: str | None = None


class BasePatchDocument(BaseContractDocument):
    documentOf: ContractDocumentOf | None = None

    @computed_field
    def dateModified(self) -> Any:
        return get_request_now().isoformat()


class BaseDocument(BaseContractDocument):
    id: MD5
    hash: Hash | None = None
    title: str
    format: str = Field(pattern=r"^[-\w]+/[-\.\w\+]+$")
    url: str
    documentOf: ContractDocumentOf = "contract"
    datePublished: str
    dateModified: str | None = None
    author: str | None = None


class PostTransactionDocument(BaseTransactionDocument, BasePostDocument):  # type: ignore[misc]
    pass


class TransactionDocument(BaseTransactionDocument, BaseDocument):  # type: ignore[misc]
    pass


class PostDocument(BasePostDocument, PostConfidentialDocumentMixin):
    pass


class PatchDocument(BasePatchDocument):
    confidentiality: ConfidentialityType | None = None
    confidentialityRationale: str | None = None


class Document(BaseDocument, ConfidentialDocumentMixin):
    pass
