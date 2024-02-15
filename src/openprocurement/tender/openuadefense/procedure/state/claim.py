from openprocurement.tender.core.procedure.state.claim import ClaimStateMixin
from openprocurement.tender.openuadefense.procedure.state.tender import (
    OpenUADefenseTenderState,
)


class OpenUADefenseTenderClaimState(ClaimStateMixin, OpenUADefenseTenderState):
    pass
