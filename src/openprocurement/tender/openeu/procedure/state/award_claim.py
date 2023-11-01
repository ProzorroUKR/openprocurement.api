from openprocurement.tender.core.procedure.state.award_claim import AwardClaimStateMixin
from openprocurement.tender.openeu.procedure.state.tender import BaseOpenEUTenderState


class OpenEUAwardClaimState(AwardClaimStateMixin, BaseOpenEUTenderState):
    pass
