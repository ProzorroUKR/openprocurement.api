from openprocurement.tender.core.procedure.state.award_complaint import (
    AwardComplaintStateMixin,
)
from openprocurement.tender.openuadefense.procedure.state.tender import (
    DefenseTenderState,
)


class DefenseAwardComplaintState(AwardComplaintStateMixin, DefenseTenderState):
    pass
