from openprocurement.tender.core.procedure.state.complaint import ComplaintStateMixin
from openprocurement.tender.open.procedure.state.tender import OpenTenderState


class OpenTenderComplaintState(ComplaintStateMixin, OpenTenderState):
    pass
