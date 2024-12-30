from openprocurement.tender.core.procedure.state.complaint import TenderComplaintState
from openprocurement.tender.openua.procedure.state.tender import OpenUATenderState


class OpenUATenderComplaintState(TenderComplaintState, OpenUATenderState):
    pass
