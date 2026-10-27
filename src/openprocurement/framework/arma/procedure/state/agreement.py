from openprocurement.framework.arma.procedure.models.agreement import Agreement
from openprocurement.framework.core.procedure.state.agreement import AgreementState


class ARMAAgreementState(AgreementState):
    data_model = Agreement
