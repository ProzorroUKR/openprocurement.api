from openprocurement.framework.arma.procedure.models.submission import PostSubmission, Submission
from openprocurement.framework.core.procedure.state.submission import SubmissionState


class ARMASubmissionState(SubmissionState):
    post_data_model = PostSubmission
    data_model = Submission
