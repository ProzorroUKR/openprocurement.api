from openprocurement.framework.core.procedure.state.submission import SubmissionState
from openprocurement.framework.dps.procedure.models.agreement import PostAgreement
from openprocurement.framework.dps.procedure.models.qualification import CreateQualification


class DPSSubmissionState(SubmissionState):
    qualification_model = CreateQualification
    agreement_model = PostAgreement
