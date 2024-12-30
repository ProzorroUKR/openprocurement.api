from openprocurement.tender.competitiveordering.procedure.state.tender import (
    OpenTenderState,
)
from openprocurement.tender.core.procedure.state.complaint import TenderComplaintState


class OpenTenderComplaintState(TenderComplaintState, OpenTenderState):
    pass
