from openprocurement.tender.competitivedialogue.procedure.state.stage2.tender import (
    CDStage2EUTenderState,
    CDStage2UATenderState,
)
from openprocurement.tender.core.procedure.state.cancellation_complaint import (
    CancellationComplaintStateMixin,
)


class CDStage2EUCancellationComplaintState(CancellationComplaintStateMixin, CDStage2EUTenderState):
    pass


class CDStage2UACancellationComplaintState(CancellationComplaintStateMixin, CDStage2UATenderState):
    pass
