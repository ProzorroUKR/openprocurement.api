from schematics.types import StringType

from openprocurement.framework.core.procedure.models.submission import (
    PostSubmission as BasePostSubmission,
    Submission as BaseSubmission,
)
from openprocurement.framework.electroniccatalogue.constants import ELECTRONIC_CATALOGUE_TYPE


class PostSubmission(BasePostSubmission):
    submissionType = StringType(default=ELECTRONIC_CATALOGUE_TYPE)


class Submission(BaseSubmission):
    submissionType = StringType(default=ELECTRONIC_CATALOGUE_TYPE)
