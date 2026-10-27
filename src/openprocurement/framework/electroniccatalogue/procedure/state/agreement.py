from openprocurement.framework.core.procedure.state.agreement import AgreementState
from openprocurement.framework.electroniccatalogue.procedure.models.agreement import Agreement


class ElectronicDialogueAgreementState(AgreementState):
    data_model = Agreement
