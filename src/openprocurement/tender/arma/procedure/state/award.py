from openprocurement.tender.arma.procedure.models.award import ARMAAward, ARMAPostAward
from openprocurement.tender.arma.procedure.state.tender import TenderState
from openprocurement.tender.openua.procedure.state.award import (
    AwardState as BaseAwardState,
)


class AwardState(BaseAwardState, TenderState):
    post_data_model = ARMAPostAward
    data_model = ARMAAward
    award_class = ARMAAward
