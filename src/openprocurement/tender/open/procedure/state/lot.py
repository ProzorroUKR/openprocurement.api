from openprocurement.tender.core.procedure.state.lot import LotStateMixin
from openprocurement.tender.open.procedure.state.tender_details import (
    AboveThresholdEUTenderDetailsState,
    AboveThresholdTenderDetailsState,
    AboveThresholdUATenderDetailsState,
    BelowThresholdTenderDetailsState,
    COLongTenderDetailsState,
    COShortTenderDetailsState,
    DefenseTenderDetailsState,
    RFPTenderDetailsState,
    SimpleDefenseTenderDetailsState,
)


class AboveThresholdTenderLotState(LotStateMixin, AboveThresholdTenderDetailsState):
    pass


class AboveThresholdUATenderLotState(LotStateMixin, AboveThresholdUATenderDetailsState):
    pass


class AboveThresholdEUTenderLotState(LotStateMixin, AboveThresholdEUTenderDetailsState):
    pass


class DefenseTenderLotState(LotStateMixin, DefenseTenderDetailsState):
    pass


class COShortTenderLotState(LotStateMixin, COShortTenderDetailsState):
    pass


class COLongTenderLotState(LotStateMixin, COLongTenderDetailsState):
    pass


class BelowThresholdTenderLotState(LotStateMixin, BelowThresholdTenderDetailsState):
    pass


class RFPTenderLotState(LotStateMixin, RFPTenderDetailsState):
    pass


class SimpleDefenseTenderLotState(LotStateMixin, SimpleDefenseTenderDetailsState):
    pass
