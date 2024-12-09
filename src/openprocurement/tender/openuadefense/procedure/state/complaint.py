from openprocurement.tender.core.procedure.state.complaint import TenderComplaintState
from openprocurement.tender.openuadefense.procedure.state.tender import (
    OpenUADefenseTenderState,
)


class OpenUADefenseTenderComplaintState(TenderComplaintState, OpenUADefenseTenderState):
    pass
