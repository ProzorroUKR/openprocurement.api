from openprocurement.tender.competitivedialogue.procedure.state.stage1.tender import CDStage1TenderState
from openprocurement.tender.core.procedure.state.complaint import ComplaintStateMixin
from logging import getLogger

LOGGER = getLogger(__name__)


class CDStage1TenderComplaintState(ComplaintStateMixin, CDStage1TenderState):
    pass
