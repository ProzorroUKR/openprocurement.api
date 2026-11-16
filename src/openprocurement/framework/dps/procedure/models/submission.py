from openprocurement.api.constants import FrameworkType
from openprocurement.framework.core.procedure.models.submission import (
    PostSubmission as BasePostSubmission,
)
from openprocurement.framework.core.procedure.models.submission import (
    Submission as BaseSubmission,
)
from openprocurement.framework.dps.constants import DPSFrameworkType


class PostSubmission(BasePostSubmission):
    submissionType: DPSFrameworkType = FrameworkType.DYNAMIC_PURCHASING_SYSTEM


class Submission(BaseSubmission):
    submissionType: DPSFrameworkType = FrameworkType.DYNAMIC_PURCHASING_SYSTEM
