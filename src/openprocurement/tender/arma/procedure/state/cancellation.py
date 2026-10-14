from openprocurement.tender.arma.procedure.state.tender import (
    ComplexAssetTenderState,
    SimpleAssetTenderState,
)
from openprocurement.tender.core.procedure.state.cancellation import CancellationStateMixin


class ARMACancellationStateMixin(CancellationStateMixin):
    cancellation_unsuccessful_items_check = True


class ComplexAssetCancellationState(ARMACancellationStateMixin, ComplexAssetTenderState):
    pass


class SimpleAssetCancellationState(ARMACancellationStateMixin, SimpleAssetTenderState):
    pass
