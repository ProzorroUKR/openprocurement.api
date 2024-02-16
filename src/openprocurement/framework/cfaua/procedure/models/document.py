from schematics.types import StringType

from openprocurement.api.procedure.models.document import Document as BaseDocument
from openprocurement.api.procedure.models.document import (
    PatchDocument as BasePatchDocument,
)
from openprocurement.api.procedure.models.document import (
    PostDocument as BasePostDocument,
)


class PostDocument(BasePostDocument):
    documentOf = StringType(
        required=True, choices=["tender", "item", "contract", "agreement", "lot", "change"], default="agreement"
    )


class PatchDocument(BasePatchDocument):
    documentOf = StringType(choices=["tender", "item", "contract", "agreement", "lot", "change"], default="agreement")


class Document(BaseDocument):
    documentOf = StringType(
        required=True, choices=["tender", "item", "contract", "agreement", "lot", "change"], default="agreement"
    )
