from openprocurement.framework.core.procedure.state.submission import SubmissionState
from openprocurement.framework.dps.procedure.models.submission import PostSubmission, Submission


class DPSSubmissionState(SubmissionState):
    post_data_model = PostSubmission
    data_model = Submission
