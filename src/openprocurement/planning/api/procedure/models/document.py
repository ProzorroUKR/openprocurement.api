from schematics.types import StringType

from openprocurement.tender.core.procedure.models.document import (
    Document as BaseDocument,
)
from openprocurement.tender.core.procedure.models.document import (
    PatchDocument as BasePatchDocument,
)
from openprocurement.tender.core.procedure.models.document import (
    PostDocument as BasePostDocument,
)


class PostDocument(BasePostDocument):
    documentOf = StringType(required=False)


class PatchDocument(BasePatchDocument):
    documentOf = StringType(required=False)


class Document(BaseDocument):
    documentOf = StringType(required=False)
