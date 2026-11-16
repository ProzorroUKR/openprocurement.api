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
    confidentiality: ConfidentialityType | None = None
    confidentialityRationale: str | None = None


class SubmissionDocument(BaseDocument, ConfidentialDocumentMixin):
    pass
