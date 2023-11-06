from openprocurement.tender.core.procedure.state.complaint import ComplaintStateMixin
from openprocurement.tender.openua.procedure.state.tender import OpenUATenderState


class OpenUATenderComplaintState(ComplaintStateMixin, OpenUATenderState):
    pass
