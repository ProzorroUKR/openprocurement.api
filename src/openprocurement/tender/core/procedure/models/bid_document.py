from schematics.types import StringType

from openprocurement.api.procedure.models.document import (
    ConfidentialDocumentMixin,
    ConfidentialityTypes,
)
from openprocurement.tender.core.procedure.models.document import (
    Document as BaseDocument,
)
from openprocurement.tender.core.procedure.models.document import (
    PatchDocument as BasePatchDocument,
)
from openprocurement.tender.core.procedure.models.document import (
    PostDocument as BasePostDocument,
)


class PostDocument(BasePostDocument, ConfidentialDocumentMixin):
    pass


class PatchDocument(BasePatchDocument):
    confidentiality = StringType(choices=[ConfidentialityTypes.PUBLIC.value, ConfidentialityTypes.BUYER_ONLY.value])
    confidentialityRationale = StringType()


class Document(BaseDocument, ConfidentialDocumentMixin):
    pass
