from typing import Literal

from openprocurement.api.procedure.models.document import Document as BaseDocument
from openprocurement.api.procedure.models.document import (
    PatchDocument as BasePatchDocument,
)
from openprocurement.api.procedure.models.document import (
    PostDocument as BasePostDocument,
)


class PostDocument(BasePostDocument):
    documentOf: Literal["tender", "item", "contract", "agreement", "lot", "change"] = "agreement"


class PatchDocument(BasePatchDocument):
    documentOf: Literal["tender", "item", "contract", "agreement", "lot", "change"] | None = None


class Document(BaseDocument):
    documentOf: Literal["tender", "item", "contract", "agreement", "lot", "change"] = "agreement"
