from openprocurement.framework.core.procedure.state.submission import SubmissionState
from openprocurement.framework.ifi.procedure.models.submission import PostSubmission, Submission


class IFISubmissionState(SubmissionState):
    post_data_model = PostSubmission
    data_model = Submission
