from openprocurement.tender.arma.procedure.state.tender import ARMATenderState
from openprocurement.tender.core.procedure.state.award_claim import AwardClaimStateMixin


class ARMAAwardClaimState(AwardClaimStateMixin, ARMATenderState):
    pass
