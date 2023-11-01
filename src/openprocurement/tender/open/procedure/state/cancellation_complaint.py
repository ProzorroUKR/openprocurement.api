from openprocurement.tender.core.procedure.state.cancellation_complaint import CancellationComplaintStateMixin
from openprocurement.tender.open.procedure.state.tender import OpenTenderState


class OpenCancellationComplaintState(CancellationComplaintStateMixin, OpenTenderState):
    pass
