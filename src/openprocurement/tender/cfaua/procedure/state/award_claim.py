from openprocurement.tender.core.procedure.state.award_claim import AwardClaimState


class CFAUAAwardClaimState(AwardClaimState):
    create_allowed_tender_statuses = ("active.qualification.stand-still",)
    update_allowed_tender_statuses = ("active.qualification.stand-still",)
    patch_as_complaint_owner_tender_statuses = ("active.qualification.stand-still",)
