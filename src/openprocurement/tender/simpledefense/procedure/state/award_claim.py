from openprocurement.tender.core.procedure.state.award_claim import AwardClaimStateMixin
from openprocurement.tender.simpledefense.procedure.state.tender import (
    SimpleDefenseTenderState,
)


class SimpleDefenseAwardClaimState(AwardClaimStateMixin, SimpleDefenseTenderState):
    award_claims_forbidden_by_date = True
