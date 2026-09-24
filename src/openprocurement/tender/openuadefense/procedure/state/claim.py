from openprocurement.tender.core.procedure.state.claim import ClaimStateMixin
from openprocurement.tender.openuadefense.procedure.state.tender import (
    DefenseTenderState,
)


class DefenseTenderClaimState(ClaimStateMixin, DefenseTenderState):
    pass
