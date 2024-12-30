from logging import getLogger

from openprocurement.tender.competitivedialogue.procedure.state.stage1.tender import (
    CDStage1TenderState,
)
from openprocurement.tender.core.procedure.state.complaint import TenderComplaintState

LOGGER = getLogger(__name__)


class CDStage1TenderComplaintState(TenderComplaintState, CDStage1TenderState):
    pass
