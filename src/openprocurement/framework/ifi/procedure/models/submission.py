from openprocurement.api.constants import FrameworkType
from openprocurement.framework.core.procedure.models.submission import (
    PostSubmission as BasePostSubmission,
)
from openprocurement.framework.core.procedure.models.submission import (
    Submission as BaseSubmission,
)
from openprocurement.framework.ifi.constants import IFIFrameworkType


class PostSubmission(BasePostSubmission):
    submissionType: IFIFrameworkType = FrameworkType.INTERNATIONAL_FINANCIAL_INSTITUTIONS


class Submission(BaseSubmission):
    submissionType: IFIFrameworkType = FrameworkType.INTERNATIONAL_FINANCIAL_INSTITUTIONS
