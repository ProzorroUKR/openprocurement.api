from openprocurement.framework.core.procedure.state.agreement import AgreementState
from openprocurement.framework.ifi.procedure.models.agreement import Agreement


class IFIAgreementState(AgreementState):
    data_model = Agreement
