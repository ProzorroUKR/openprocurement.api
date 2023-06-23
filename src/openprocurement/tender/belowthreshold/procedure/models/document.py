from openprocurement.tender.openua.procedure.models.document import (
    PostDocument as BasePostDocument,
    PatchDocument as BasePatchDocument,
    Document as BaseDocument,
)
from schematics.types import StringType


class PostDocument(BasePostDocument):
    language = StringType(required=True, choices=["uk", "en", "ru"], default="uk")


class PatchDocument(BasePatchDocument):
    pass


class Document(BaseDocument):
    pass
