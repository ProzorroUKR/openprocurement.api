from schematics.types import StringType

from openprocurement.framework.core.procedure.models.submission import (
    PostSubmission as BasePostSubmission,
    Submission as BaseSubmission,
)
from openprocurement.framework.dps.constants import DPS_TYPE


class PostSubmission(BasePostSubmission):
    submissionType = StringType(default=DPS_TYPE)


class Submission(BaseSubmission):
    submissionType = StringType(default=DPS_TYPE)
