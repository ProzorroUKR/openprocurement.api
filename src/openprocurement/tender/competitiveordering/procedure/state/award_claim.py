from openprocurement.tender.competitiveordering.procedure.state.tender import (
    OpenTenderState,
)
from openprocurement.tender.core.procedure.state.award_claim import AwardClaimStateMixin


class OpenAwardClaimState(AwardClaimStateMixin, OpenTenderState):
    pass
