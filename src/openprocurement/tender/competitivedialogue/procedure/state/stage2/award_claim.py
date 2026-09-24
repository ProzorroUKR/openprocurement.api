from openprocurement.tender.competitivedialogue.procedure.state.stage2.tender import (
    CDStage2EUTenderState,
    CDStage2UATenderState,
)
from openprocurement.tender.core.procedure.state.award_claim import AwardClaimStateMixin


class CDStage2UAAwardClaimState(AwardClaimStateMixin, CDStage2UATenderState):
    pass


class CDStage2EUAwardClaimState(AwardClaimStateMixin, CDStage2EUTenderState):
    pass
