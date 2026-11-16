from openprocurement.api.constants import FrameworkType
from openprocurement.framework.arma.constants import ARMAFrameworkType
from openprocurement.framework.core.procedure.models.submission import (
    PostSubmission as BasePostSubmission,
)
from openprocurement.framework.core.procedure.models.submission import (
    Submission as BaseSubmission,
)


class PostSubmission(BasePostSubmission):
    submissionType: ARMAFrameworkType = FrameworkType.ASSET_RECOVERY_MANAGEMENT_AGENCY


class Submission(BaseSubmission):
    submissionType: ARMAFrameworkType = FrameworkType.ASSET_RECOVERY_MANAGEMENT_AGENCY
