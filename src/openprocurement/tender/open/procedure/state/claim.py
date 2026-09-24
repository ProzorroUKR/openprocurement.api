from openprocurement.tender.core.procedure.state.claim import ClaimStateMixin
from openprocurement.tender.open.constants import (
    ABOVE_THRESHOLD_EU_CLAIM_SUBMIT_TIME,
    ABOVE_THRESHOLD_UA_CLAIM_SUBMIT_TIME,
)
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


class AboveThresholdTenderClaimState(ClaimStateMixin, AboveThresholdTenderState):
    pass


class AboveThresholdUATenderClaimState(ClaimStateMixin, AboveThresholdUATenderState):
    tender_claim_submit_time = ABOVE_THRESHOLD_UA_CLAIM_SUBMIT_TIME


class AboveThresholdEUTenderClaimState(ClaimStateMixin, AboveThresholdEUTenderState):
    tender_claim_submit_time = ABOVE_THRESHOLD_EU_CLAIM_SUBMIT_TIME


class DefenseTenderClaimState(ClaimStateMixin, DefenseTenderState):
    pass


class SimpleDefenseTenderClaimState(ClaimStateMixin, SimpleDefenseTenderState):
    pass


class COTenderClaimState(ClaimStateMixin, COTenderState):
    pass


class BelowThresholdTenderClaimState(ClaimStateMixin, BelowThresholdTenderState):
    complaint_patch_allowed_tender_statuses = (
        "active.enquiries",
        "active.tendering",
        "active.auction",
        "active.qualification",
        "active.awarded",
    )
    patch_as_complaint_owner_tender_statuses = (
        "active.enquiries",
        "active.tendering",
    )
    is_satisfied_check = False
    claim_submit_check = False


class RFPTenderClaimState(ClaimStateMixin, RFPTenderState):
    complaint_patch_allowed_tender_statuses = (
        "active.enquiries",
        "active.tendering",
        "active.auction",
        "active.qualification",
        "active.awarded",
    )
    patch_as_complaint_owner_tender_statuses = (
        "active.enquiries",
        "active.tendering",
    )
    is_satisfied_check = False
    claim_submit_check = False
