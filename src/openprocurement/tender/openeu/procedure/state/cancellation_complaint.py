from openprocurement.tender.core.procedure.state.cancellation_complaint import (
    CancellationComplaintStateMixin,
)
from openprocurement.tender.openeu.procedure.state.tender import OpenEUTenderState


class OpenEUCancellationComplaintState(CancellationComplaintStateMixin, OpenEUTenderState):
    pass
