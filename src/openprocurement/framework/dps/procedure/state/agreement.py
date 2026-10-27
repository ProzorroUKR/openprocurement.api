from openprocurement.framework.core.procedure.state.agreement import AgreementState
from openprocurement.framework.dps.procedure.models.agreement import Agreement


class DPSAgreementState(AgreementState):
    data_model = Agreement
