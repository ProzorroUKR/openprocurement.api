from openprocurement.tender.core.procedure.state.claim import ClaimStateMixin
from openprocurement.tender.open.procedure.state.tender import OpenTenderState


class OpenTenderClaimState(ClaimStateMixin, OpenTenderState):
    pass
