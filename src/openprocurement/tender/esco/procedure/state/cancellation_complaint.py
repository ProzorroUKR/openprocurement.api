from openprocurement.tender.core.procedure.state.cancellation_complaint import (
    CancellationComplaintStateMixin,
)
from openprocurement.tender.esco.procedure.state.complaint import (
    ESCOComplaintStateMixin,
)
from openprocurement.tender.esco.procedure.state.tender import ESCOTenderState


class ESCOCancellationComplaintState(ESCOComplaintStateMixin, CancellationComplaintStateMixin, ESCOTenderState):
    pass
