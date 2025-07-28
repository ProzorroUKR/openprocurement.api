from logging import getLogger

from openprocurement.tender.cfaua.procedure.state.tender import CFAUATenderState
from openprocurement.tender.core.procedure.state.complaint import TenderComplaintState

LOGGER = getLogger(__name__)


class CFAUATenderComplaintState(TenderComplaintState, CFAUATenderState):
    all_documents_should_be_public = True
