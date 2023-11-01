from openprocurement.tender.cfaua.procedure.state.tender import CFAUATenderState
from openprocurement.tender.core.procedure.state.complaint import ComplaintStateMixin
from logging import getLogger

LOGGER = getLogger(__name__)


class CFAUATenderComplaintState(ComplaintStateMixin, CFAUATenderState):
    pass
