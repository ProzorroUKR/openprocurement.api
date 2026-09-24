from openprocurement.tender.cfaua.procedure.state.tender import CFAUATenderState
from openprocurement.tender.core.procedure.state.award_claim import AwardClaimStateMixin


class CFAUAAwardClaimState(AwardClaimStateMixin, CFAUATenderState):
    complaint_post_allowed_tender_statuses = ("active.qualification.stand-still",)
    complaint_patch_allowed_tender_statuses = ("active.qualification.stand-still",)
    patch_as_complaint_owner_tender_statuses = ("active.qualification.stand-still",)
