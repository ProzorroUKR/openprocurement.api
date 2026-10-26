from openprocurement.tender.arma.procedure.state.tender import (
    ComplexAssetTenderState,
    SimpleAssetTenderState,
)
from openprocurement.tender.core.procedure.state.complaint import TenderComplaintState


class ComplexAssetComplaintState(TenderComplaintState, ComplexAssetTenderState):
    pass


class SimpleAssetComplaintState(TenderComplaintState, SimpleAssetTenderState):
    pass
