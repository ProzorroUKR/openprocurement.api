from schematics.types import StringType

from openprocurement.framework.core.procedure.models.submission import (
    PostSubmission as BasePostSubmission,
)
from openprocurement.framework.core.procedure.models.submission import (
    Submission as BaseSubmission,
)
from openprocurement.framework.ifi.constants import IFI_TYPE


class PostSubmission(BasePostSubmission):
    submissionType = StringType(default=IFI_TYPE)


class Submission(BaseSubmission):
    submissionType = StringType(default=IFI_TYPE)
