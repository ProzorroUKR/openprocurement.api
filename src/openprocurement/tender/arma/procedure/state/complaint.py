from openprocurement.tender.arma.procedure.state.tender import ARMATenderState
from openprocurement.tender.core.procedure.state.complaint import TenderComplaintState


class ARMAComplaintState(TenderComplaintState, ARMATenderState):
    pass
