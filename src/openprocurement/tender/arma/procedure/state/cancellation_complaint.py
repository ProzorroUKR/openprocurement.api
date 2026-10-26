from openprocurement.tender.arma.procedure.state.tender import (
    ComplexAssetTenderState,
    SimpleAssetTenderState,
)
from openprocurement.tender.core.procedure.state.cancellation_complaint import (
    CancellationComplaintStateMixin,
)


class ComplexAssetCancellationComplaintState(CancellationComplaintStateMixin, ComplexAssetTenderState):
    pass


class SimpleAssetCancellationComplaintState(CancellationComplaintStateMixin, SimpleAssetTenderState):
    pass
