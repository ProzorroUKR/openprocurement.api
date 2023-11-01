from openprocurement.tender.core.procedure.state.complaint import ComplaintStateMixin
from openprocurement.tender.simpledefense.procedure.state.tender import SimpleDefenseTenderState


class SimpleDefenseTenderComplaintState(ComplaintStateMixin, SimpleDefenseTenderState):
    pass
