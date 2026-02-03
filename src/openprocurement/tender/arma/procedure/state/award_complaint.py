from openprocurement.tender.arma.procedure.state.tender import TenderState
from openprocurement.tender.core.procedure.state.award_complaint import (
    AwardComplaintStateMixin,
)


class AwardComplaintState(AwardComplaintStateMixin, TenderState):
    pass
