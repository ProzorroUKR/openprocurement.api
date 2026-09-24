from logging import getLogger

from openprocurement.tender.core.procedure.state.complaint import TenderComplaintState
from openprocurement.tender.open.procedure.state.tender import (
    AboveThresholdEUTenderState,
    AboveThresholdTenderState,
    AboveThresholdUATenderState,
    COTenderState,
    DefenseTenderState,
    SimpleDefenseTenderState,
)


class AboveThresholdTenderComplaintState(TenderComplaintState, AboveThresholdTenderState):
    pass


class AboveThresholdUATenderComplaintState(TenderComplaintState, AboveThresholdUATenderState):
    pass


LOGGER = getLogger(__name__)


class AboveThresholdEUTenderComplaintState(TenderComplaintState, AboveThresholdEUTenderState):
    pass


class DefenseTenderComplaintState(TenderComplaintState, DefenseTenderState):
    pass


class SimpleDefenseTenderComplaintState(TenderComplaintState, SimpleDefenseTenderState):
    pass


class COTenderComplaintState(TenderComplaintState, COTenderState):
    complaint_author_qualified_supplier_check = True
