from openprocurement.tender.core.procedure.state.award_complaint import AwardComplaintStateMixin
from openprocurement.tender.openuadefense.procedure.state.tender import OpenUADefenseTenderState


class OpenUADefenseAwardComplaintState(AwardComplaintStateMixin, OpenUADefenseTenderState):
    pass
