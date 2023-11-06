from openprocurement.tender.core.procedure.state.claim import ClaimStateMixin
from openprocurement.tender.simpledefense.procedure.state.tender import SimpleDefenseTenderState


class SimpleDefenseTenderClaimState(ClaimStateMixin, SimpleDefenseTenderState):
    pass
