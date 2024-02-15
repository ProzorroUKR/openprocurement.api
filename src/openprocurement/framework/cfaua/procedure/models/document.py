from schematics.types import StringType
from openprocurement.api.procedure.models.document import (
    PostDocument as BasePostDocument,
    PatchDocument as BasePatchDocument,
    Document as BaseDocument,
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
