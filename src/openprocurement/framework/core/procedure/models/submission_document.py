from schematics.types import StringType

from openprocurement.api.procedure.models.document import (
    ConfidentialDocumentMixin,
    ConfidentialityType,
    PatchDocument,
    PostConfidentialDocumentMixin,
    PostDocument,
)
from openprocurement.api.procedure.models.document import (
    Document as BaseDocument,
)


class PostSubmissionDocument(PostDocument, PostConfidentialDocumentMixin):
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
