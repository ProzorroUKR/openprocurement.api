from openprocurement.tender.arma.procedure.state.tender import ARMATenderState
from openprocurement.tender.core.procedure.state.award_complaint import (
    AwardComplaintStateMixin,
)


class ARMAAwardComplaintState(AwardComplaintStateMixin, ARMATenderState):
    pass
