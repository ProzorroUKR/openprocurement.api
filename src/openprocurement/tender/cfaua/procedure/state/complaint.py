from logging import getLogger

from openprocurement.tender.cfaua.procedure.state.tender import CFAUATenderState
from openprocurement.tender.core.procedure.state.complaint import ComplaintStateMixin

LOGGER = getLogger(__name__)


class CFAUATenderComplaintState(ComplaintStateMixin, CFAUATenderState):
    pass
