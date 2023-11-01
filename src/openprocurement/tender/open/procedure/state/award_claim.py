from openprocurement.tender.core.procedure.state.award_claim import AwardClaimStateMixin
from openprocurement.tender.open.procedure.state.tender import OpenTenderState


class OpenAwardClaimState(AwardClaimStateMixin, OpenTenderState):
    pass
