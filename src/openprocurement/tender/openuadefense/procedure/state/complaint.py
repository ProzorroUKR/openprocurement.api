from openprocurement.tender.core.procedure.state.complaint import TenderComplaintState
from openprocurement.tender.openuadefense.procedure.state.tender import (
    DefenseTenderState,
)


class DefenseTenderComplaintState(TenderComplaintState, DefenseTenderState):
    pass
