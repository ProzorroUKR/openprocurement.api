from openprocurement.tender.arma.procedure.state.tender import (
    ComplexAssetTenderState,
    SimpleAssetTenderState,
)
from openprocurement.tender.core.procedure.state.award_complaint import (
    AwardComplaintStateMixin,
)


class ComplexAssetAwardComplaintState(AwardComplaintStateMixin, ComplexAssetTenderState):
    pass


class SimpleAssetAwardComplaintState(AwardComplaintStateMixin, SimpleAssetTenderState):
    pass
