from openprocurement.tender.belowthreshold.procedure.state.tender import (
    BelowThresholdTenderState,
)
from openprocurement.tender.core.procedure.state.claim import ClaimStateMixin


class BelowThresholdTenderClaimState(ClaimStateMixin, BelowThresholdTenderState):
    update_allowed_tender_statuses = (
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

    def validate_submit_claim(self, claim):
        pass

    def validate_satisfied(self, satisfied):
        return isinstance(satisfied, bool)
