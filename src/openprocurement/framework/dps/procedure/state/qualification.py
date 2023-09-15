from openprocurement.framework.core.procedure.state.qualification import QualificationState
from openprocurement.framework.dps.models import Submission
from openprocurement.framework.dps.procedure.models.agreement import PostAgreement


class DPSQualificationState(QualificationState):
    submission_model = Submission
    agreement_model = PostAgreement
