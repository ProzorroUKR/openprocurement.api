from openprocurement.tender.arma.procedure.models.award import Award
from openprocurement.tender.arma.procedure.state.tender import TenderState
from openprocurement.tender.openua.procedure.state.award import (
    AwardState as BaseAwardState,
)


class AwardState(BaseAwardState, TenderState):
    award_class = Award
