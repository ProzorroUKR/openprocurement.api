from schematics.types import StringType

from openprocurement.api.procedure.models.document import (
    ConfidentialDocumentMixin,
    ConfidentialityType,
)
from openprocurement.api.procedure.models.document import Document as BaseDocument
from openprocurement.api.procedure.models.document import PatchDocument, PostDocument


class PostSubmissionDocument(PostDocument, ConfidentialDocumentMixin):
    pass


class PatchSubmissionDocument(PatchDocument):
    confidentiality = StringType(
        choices=[
            ConfidentialityType.PUBLIC.value,
            ConfidentialityType.BUYER_ONLY.value,
        ]
    )
    confidentialityRationale = StringType()


class SubmissionDocument(BaseDocument, ConfidentialDocumentMixin):
    pass
