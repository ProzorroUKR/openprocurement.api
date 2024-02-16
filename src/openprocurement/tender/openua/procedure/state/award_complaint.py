from openprocurement.tender.core.procedure.state.award_complaint import (
    AwardComplaintStateMixin,
)
from openprocurement.tender.openua.procedure.state.tender import OpenUATenderState


class OpenUAAwardComplaintState(AwardComplaintStateMixin, OpenUATenderState):
    pass
