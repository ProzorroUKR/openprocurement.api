from schematics.types import StringType

from openprocurement.api.procedure.models.document import (
    ConfidentialDocumentMixin,
    ConfidentialityTypes,
)
from openprocurement.api.procedure.models.document import Document as BaseDocument
from openprocurement.api.procedure.models.document import PatchDocument, PostDocument


class PostSubmissionDocument(PostDocument, ConfidentialDocumentMixin):
    pass


class PatchSubmissionDocument(PatchDocument):
    confidentiality = StringType(
        choices=[
            ConfidentialityTypes.PUBLIC.value,
            ConfidentialityTypes.BUYER_ONLY.value,
        ]
    )
    confidentialityRationale = StringType()


class SubmissionDocument(BaseDocument, ConfidentialDocumentMixin):
    pass
