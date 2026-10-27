from openprocurement.framework.core.procedure.state.submission import SubmissionState
from openprocurement.framework.electroniccatalogue.procedure.models.submission import PostSubmission, Submission


class ElectronicDialogueSubmissionState(SubmissionState):
    post_data_model = PostSubmission
    data_model = Submission
