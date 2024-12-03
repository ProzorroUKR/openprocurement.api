from openprocurement.tender.competitiveordering.procedure.state.tender import (
    OpenTenderState,
)
from openprocurement.tender.core.procedure.state.claim import ClaimStateMixin


class OpenTenderClaimState(ClaimStateMixin, OpenTenderState):
    pass
