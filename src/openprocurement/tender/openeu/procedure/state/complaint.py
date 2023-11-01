from openprocurement.tender.core.procedure.state.complaint import ComplaintStateMixin
from openprocurement.tender.openeu.procedure.state.tender import BaseOpenEUTenderState
from logging import getLogger

LOGGER = getLogger(__name__)


class OpenEUTenderComplaintState(ComplaintStateMixin, BaseOpenEUTenderState):
    pass
