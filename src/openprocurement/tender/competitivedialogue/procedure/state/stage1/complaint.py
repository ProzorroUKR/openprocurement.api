from logging import getLogger

from openprocurement.tender.competitivedialogue.procedure.state.stage1.tender import (
    CDStage1TenderState,
)
from openprocurement.tender.core.procedure.state.complaint import ComplaintStateMixin

LOGGER = getLogger(__name__)


class CDStage1TenderComplaintState(ComplaintStateMixin, CDStage1TenderState):
    pass
