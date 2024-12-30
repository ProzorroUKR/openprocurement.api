from openprocurement.tender.core.procedure.state.complaint import TenderComplaintState
from openprocurement.tender.open.procedure.state.tender import OpenTenderState


class OpenTenderComplaintState(TenderComplaintState, OpenTenderState):
    pass
