from openprocurement.tender.competitivedialogue.procedure.state.stage2.tender import (
    CDEUStage2TenderState,
    CDUAStage2TenderState,
)
from openprocurement.tender.core.procedure.state.cancellation_complaint import CancellationComplaintStateMixin


class CDEUStage2CancellationComplaintState(CancellationComplaintStateMixin, CDEUStage2TenderState):
    pass


class CDUAStage2CancellationComplaintState(CancellationComplaintStateMixin, CDUAStage2TenderState):
    pass
