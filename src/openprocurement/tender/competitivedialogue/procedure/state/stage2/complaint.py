from openprocurement.tender.competitivedialogue.procedure.state.stage2.tender import (
    CDStage2EUTenderState,
    CDStage2UATenderState,
)
from openprocurement.tender.core.procedure.state.complaint import TenderComplaintState


class CDStage2UATenderComplaintState(TenderComplaintState, CDStage2UATenderState):
    pass


class CDStage2EUTenderComplaintState(TenderComplaintState, CDStage2EUTenderState):
    pass
