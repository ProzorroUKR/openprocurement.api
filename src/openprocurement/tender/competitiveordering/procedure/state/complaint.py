from openprocurement.tender.competitiveordering.procedure.state.tender import (
    OpenTenderState,
)
from openprocurement.tender.core.procedure.state.complaint import ComplaintStateMixin


class OpenTenderComplaintState(ComplaintStateMixin, OpenTenderState):
    pass
