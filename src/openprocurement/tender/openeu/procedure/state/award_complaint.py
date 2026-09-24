from openprocurement.tender.core.procedure.state.award_complaint import (
    AwardComplaintStateMixin,
)
from openprocurement.tender.openeu.procedure.state.tender import OpenEUTenderState


class OpenEUAwardComplaintState(AwardComplaintStateMixin, OpenEUTenderState):
    pass
