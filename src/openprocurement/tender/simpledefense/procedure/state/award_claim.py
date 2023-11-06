from openprocurement.tender.core.procedure.state.award_claim import AwardClaimStateMixin
from openprocurement.tender.openuadefense.procedure.state.award_claim import DefenseAwardClaimStateMixin
from openprocurement.tender.simpledefense.procedure.state.tender import SimpleDefenseTenderState


class SimpleDefenseAwardClaimState(DefenseAwardClaimStateMixin, AwardClaimStateMixin, SimpleDefenseTenderState):
    pass
