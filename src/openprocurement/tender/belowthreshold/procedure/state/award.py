from openprocurement.tender.belowthreshold.procedure.state.tender import BelowThresholdTenderState
from openprocurement.tender.core.procedure.state.award import AwardStateMixing
from openprocurement.tender.belowthreshold.constants import STAND_STILL_TIME


class AwardState(AwardStateMixing, BelowThresholdTenderState):
    award_stand_still_time = STAND_STILL_TIME
