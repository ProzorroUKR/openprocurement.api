from openprocurement.tender.core.procedure.state.claim import ClaimState


class BelowThresholdTenderClaimState(ClaimState):
    create_allowed_tender_statuses = ("active.enquiries",)
    update_allowed_tender_statuses = (
        "active.enquiries",
        "active.tendering",
        "active.auction",
        "active.qualification",
        "active.awarded",
    )
    patch_as_complaint_owner_tender_statuses = ("active.enquiries", "active.tendering",)

    def validate_satisfied(self, satisfied):
        return isinstance(satisfied, bool)
