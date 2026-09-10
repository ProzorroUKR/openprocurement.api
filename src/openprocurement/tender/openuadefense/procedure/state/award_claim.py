from openprocurement.tender.core.procedure.state.award_claim import AwardClaimStateMixin
from openprocurement.tender.openuadefense.procedure.state.tender import (
    OpenUADefenseTenderState,
)


class DefenseAwardClaimStateMixin:
    award_claims_forbidden_by_date = True


class OpenUADefenseAwardClaimState(DefenseAwardClaimStateMixin, AwardClaimStateMixin, OpenUADefenseTenderState):
    pass
