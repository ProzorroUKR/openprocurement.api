from openprocurement.tender.core.procedure.state.award_claim import AwardClaimStateMixin
from openprocurement.tender.open.procedure.state.tender import (
    AboveThresholdEUTenderState,
    AboveThresholdTenderState,
    AboveThresholdUATenderState,
    BelowThresholdTenderState,
    COTenderState,
    DefenseTenderState,
    RFPTenderState,
    SimpleDefenseTenderState,
)


class AboveThresholdAwardClaimState(AwardClaimStateMixin, AboveThresholdTenderState):
    pass


class AboveThresholdUAAwardClaimState(AwardClaimStateMixin, AboveThresholdUATenderState):
    pass


class AboveThresholdEUAwardClaimState(AwardClaimStateMixin, AboveThresholdEUTenderState):
    pass


class DefenseAwardClaimStateMixin:
    award_claims_forbidden_by_date = True


class DefenseAwardClaimState(DefenseAwardClaimStateMixin, AwardClaimStateMixin, DefenseTenderState):
    pass


class SimpleDefenseAwardClaimState(AwardClaimStateMixin, SimpleDefenseTenderState):
    award_claims_forbidden_by_date = True


class COAwardClaimState(AwardClaimStateMixin, COTenderState):
    pass


class BelowThresholdAwardClaimState(AwardClaimStateMixin, BelowThresholdTenderState):
    complaint_post_bid_owner_statuses = ("active", "unsuccessful")
    is_satisfied_check = False
    claim_submit_check = False


class RFPAwardClaimState(AwardClaimStateMixin, RFPTenderState):
    complaint_post_bid_owner_statuses = ("active", "unsuccessful")
    is_satisfied_check = False
    claim_submit_check = False
