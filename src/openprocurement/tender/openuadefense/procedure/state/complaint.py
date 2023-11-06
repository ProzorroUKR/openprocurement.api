from openprocurement.tender.core.procedure.state.complaint import ComplaintStateMixin
from openprocurement.tender.openuadefense.procedure.state.tender import OpenUADefenseTenderState


class OpenUADefenseTenderComplaintState(ComplaintStateMixin, OpenUADefenseTenderState):
    pass
