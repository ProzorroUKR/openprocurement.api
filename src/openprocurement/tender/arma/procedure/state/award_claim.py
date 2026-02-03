from openprocurement.tender.arma.procedure.state.tender import TenderState
from openprocurement.tender.core.procedure.state.award_claim import AwardClaimStateMixin


class AwardClaimState(AwardClaimStateMixin, TenderState):
    pass
