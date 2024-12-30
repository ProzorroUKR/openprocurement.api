from openprocurement.tender.core.procedure.state.complaint import TenderComplaintState
from openprocurement.tender.simpledefense.procedure.state.tender import (
    SimpleDefenseTenderState,
)


class SimpleDefenseTenderComplaintState(TenderComplaintState, SimpleDefenseTenderState):
    pass
