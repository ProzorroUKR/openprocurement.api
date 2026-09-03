from openprocurement.tender.arma.procedure.state.tender import TenderState
from openprocurement.tender.core.procedure.models.award import ARMAAward as Award
from openprocurement.tender.openua.procedure.state.award import (
    AwardState as BaseAwardState,
)


class AwardState(BaseAwardState, TenderState):
    award_class = Award
