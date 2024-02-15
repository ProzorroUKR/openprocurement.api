from openprocurement.tender.core.procedure.state.award_complaint import (
    AwardComplaintStateMixin,
)
from openprocurement.tender.simpledefense.procedure.state.tender import (
    SimpleDefenseTenderState,
)


class SimpleDefenseAwardComplaintState(AwardComplaintStateMixin, SimpleDefenseTenderState):
    pass
