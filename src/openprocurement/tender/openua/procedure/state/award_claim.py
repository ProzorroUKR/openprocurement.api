from openprocurement.tender.core.procedure.state.award_claim import AwardClaimStateMixin
from openprocurement.tender.openua.procedure.state.tender import OpenUATenderState


class OpenUAAwardClaimState(AwardClaimStateMixin, OpenUATenderState):
    pass
