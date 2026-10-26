from openprocurement.tender.arma.procedure.state.tender import (
    ComplexAssetTenderState,
    SimpleAssetTenderState,
)
from openprocurement.tender.core.procedure.state.award_claim import AwardClaimStateMixin


class ComplexAssetAwardClaimState(AwardClaimStateMixin, ComplexAssetTenderState):
    pass


class SimpleAssetAwardClaimState(AwardClaimStateMixin, SimpleAssetTenderState):
    pass
