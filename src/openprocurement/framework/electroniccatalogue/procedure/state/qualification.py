from openprocurement.framework.core.procedure.state.qualification import QualificationState
from openprocurement.framework.electroniccatalogue.models import Submission
from openprocurement.framework.electroniccatalogue.procedure.models.agreement import PostAgreement


class ElectronicDialogueQualificationState(QualificationState):
    submission_model = Submission
    agreement_model = PostAgreement
