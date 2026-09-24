from openprocurement.tender.competitivedialogue.procedure.state.stage2.tender import (
    CDStage2EUTenderState,
    CDStage2UATenderState,
)
from openprocurement.tender.core.procedure.state.award_complaint import (
    AwardComplaintStateMixin,
)


class CDStage2UAAwardComplaintState(AwardComplaintStateMixin, CDStage2UATenderState):
    pass


class CDStage2EUAwardComplaintState(AwardComplaintStateMixin, CDStage2EUTenderState):
    pass
