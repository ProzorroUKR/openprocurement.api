from openprocurement.tender.arma.procedure.state.tender import TenderState
from openprocurement.tender.core.procedure.state.complaint import TenderComplaintState


class ComplaintState(TenderComplaintState, TenderState):
    pass
