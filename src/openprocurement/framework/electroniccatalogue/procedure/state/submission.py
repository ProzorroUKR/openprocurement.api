from openprocurement.framework.core.procedure.state.submission import SubmissionState
from openprocurement.framework.electroniccatalogue.procedure.models.agreement import PostAgreement
from openprocurement.framework.electroniccatalogue.procedure.models.qualification import CreateQualification


class ElectronicDialogueSubmissionState(SubmissionState):
    qualification_model = CreateQualification
    agreement_model = PostAgreement
