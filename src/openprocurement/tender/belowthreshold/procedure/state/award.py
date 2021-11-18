from openprocurement.tender.core.procedure.state.tender import TenderState
from openprocurement.tender.core.procedure.state.award import AwardStateMixing
from openprocurement.tender.belowthreshold.constants import STAND_STILL_TIME


class AwardState(AwardStateMixing, TenderState):
    award_stand_still_time = STAND_STILL_TIME

