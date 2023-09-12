from openprocurement.tender.core.procedure.state.cancellation_complaint import CancellationComplaintState
from openprocurement.tender.esco.procedure.state.complaint import ESCOComplaintMixin


class ESCOCancellationComplaintState(ESCOComplaintMixin, CancellationComplaintState):
    pass
