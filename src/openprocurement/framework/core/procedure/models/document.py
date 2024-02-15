from openprocurement.api.procedure.models.document import Document as BaseDocument
from openprocurement.api.procedure.models.document import (
    PatchDocument as BasePatchDocument,
)
from openprocurement.api.procedure.models.document import (
    PostDocument as BasePostDocument,
)


class PostDocument(BasePostDocument):
    pass


class PatchDocument(BasePatchDocument):
    pass


class Document(BaseDocument):
    pass
