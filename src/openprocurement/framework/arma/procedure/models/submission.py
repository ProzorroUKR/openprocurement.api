from schematics.types import StringType

from openprocurement.framework.arma.constants import ARMA_TYPE
from openprocurement.framework.core.procedure.models.submission import (
    PostSubmission as BasePostSubmission,
)
from openprocurement.framework.core.procedure.models.submission import (
    Submission as BaseSubmission,
)


class PostSubmission(BasePostSubmission):
    submissionType = StringType(default=ARMA_TYPE)


class Submission(BaseSubmission):
    submissionType = StringType(default=ARMA_TYPE)
