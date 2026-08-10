from openprocurement.tender.belowthreshold.procedure.state.tender import (
    BelowThresholdTenderState,
)
from openprocurement.tender.core.procedure.state.award import AwardStateMixing


class AwardState(AwardStateMixing, BelowThresholdTenderState):
    pass
