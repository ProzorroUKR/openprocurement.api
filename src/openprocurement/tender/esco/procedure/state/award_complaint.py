from openprocurement.tender.core.procedure.state.award_complaint import (
    AwardComplaintStateMixin,
)
from openprocurement.tender.esco.procedure.state.complaint import (
    ESCOComplaintStateMixin,
)
from openprocurement.tender.esco.procedure.state.tender import ESCOTenderState


class ESCOAwardComplaintState(ESCOComplaintStateMixin, AwardComplaintStateMixin, ESCOTenderState):
    pass
