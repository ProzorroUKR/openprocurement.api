from openprocurement.tender.arma.constants import ARMA_CLAIM_SUBMIT_TIME
from openprocurement.tender.arma.procedure.state.tender import (
    ComplexAssetTenderState,
    SimpleAssetTenderState,
)
from openprocurement.tender.core.procedure.state.claim import ClaimStateMixin


class ARMAClaimStateMixin(ClaimStateMixin):
    tender_claim_submit_time = ARMA_CLAIM_SUBMIT_TIME


class ComplexAssetClaimState(ARMAClaimStateMixin, ComplexAssetTenderState):
    pass


class SimpleAssetClaimState(ARMAClaimStateMixin, SimpleAssetTenderState):
    pass
