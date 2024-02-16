from openprocurement.tender.core.procedure.state.award_complaint import (
    AwardComplaintStateMixin,
)
from openprocurement.tender.open.procedure.state.tender import OpenTenderState


class OpenAwardComplaintState(AwardComplaintStateMixin, OpenTenderState):
    pass
