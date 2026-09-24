from openprocurement.tender.core.procedure.models.award import Award
from openprocurement.tender.core.procedure.state.lot import LotStateMixin
from openprocurement.tender.core.procedure.state.tender import TenderState
from openprocurement.tender.core.procedure.state.tender_details import TenderDetailsMixin
from openprocurement.tender.open.constants import ABOVE_THRESHOLD_UA_DEFENSE_LOT_TENDERING_EXTRA_PERIOD
from openprocurement.tender.open.procedure.state.tender_details import (
    AboveThresholdEUTenderDetailsState,
    AboveThresholdTenderDetailsState,
    AboveThresholdUATenderDetailsState,
    BelowThresholdTenderDetailsState,
    COLongTenderDetailsState,
    COShortTenderDetailsState,
    RFPTenderDetailsState,
)


class AboveThresholdTenderLotState(LotStateMixin, AboveThresholdTenderDetailsState):
    pass


class AboveThresholdUATenderLotState(LotStateMixin, AboveThresholdUATenderDetailsState):
    pass


class AboveThresholdEUTenderLotState(LotStateMixin, AboveThresholdEUTenderDetailsState):
    pass


class DefenseTenderLotState(LotStateMixin, TenderDetailsMixin, TenderState):
    award_class = Award

    tender_period_extra = ABOVE_THRESHOLD_UA_DEFENSE_LOT_TENDERING_EXTRA_PERIOD
    contract_template_required = True


class COShortTenderLotState(LotStateMixin, COShortTenderDetailsState):
    pass


class COLongTenderLotState(LotStateMixin, COLongTenderDetailsState):
    pass


class BelowThresholdTenderLotState(LotStateMixin, BelowThresholdTenderDetailsState):
    lot_operation_allowed_tender_statuses = ("active.enquiries", "draft")
    invalidate_bids_on_lot_change = False


class RFPTenderLotState(LotStateMixin, RFPTenderDetailsState):
    lot_operation_allowed_tender_statuses = ("active.enquiries", "active.tendering", "draft")
    invalidate_bids_on_lot_change = False
