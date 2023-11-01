from openprocurement.tender.core.procedure.state.award_claim import AwardClaimStateMixin
from openprocurement.tender.esco.procedure.state.tender import ESCOTenderState


class ESCOAwardClaimState(AwardClaimStateMixin, ESCOTenderState):
    pass
