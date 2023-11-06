from openprocurement.tender.competitivedialogue.procedure.state.stage1.tender import CDStage1TenderState
from openprocurement.tender.core.procedure.state.cancellation_complaint import CancellationComplaintStateMixin


class CDStage1CancellationComplaintState(CancellationComplaintStateMixin, CDStage1TenderState):
    pass
