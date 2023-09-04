from openprocurement.tender.core.procedure.state.award_complaint import AwardComplaintState
from openprocurement.tender.esco.procedure.state.complaint import ESCOComplaintMixin


class ESCOAwardComplaintState(ESCOComplaintMixin, AwardComplaintState):
    pass
