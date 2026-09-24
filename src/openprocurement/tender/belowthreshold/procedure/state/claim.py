from openprocurement.tender.belowthreshold.procedure.state.tender import (
    BelowThresholdTenderState,
)
from openprocurement.tender.core.procedure.state.claim import ClaimStateMixin


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
