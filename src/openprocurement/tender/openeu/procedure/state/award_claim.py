from openprocurement.tender.core.procedure.state.award_claim import AwardClaimStateMixin
from openprocurement.tender.openeu.procedure.state.tender import OpenEUTenderState


class OpenEUAwardClaimState(AwardClaimStateMixin, OpenEUTenderState):
    pass
