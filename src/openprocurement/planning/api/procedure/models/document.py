from schematics.types import StringType

from openprocurement.tender.core.procedure.models.document import (
    PostDocument as BasePostDocument,
    PatchDocument as BasePatchDocument,
    Document as BaseDocument,
)


class PostDocument(BasePostDocument):
    documentOf = StringType(required=False)


class PatchDocument(BasePatchDocument):
    documentOf = StringType(required=False)


class Document(BaseDocument):
    documentOf = StringType(required=False)
