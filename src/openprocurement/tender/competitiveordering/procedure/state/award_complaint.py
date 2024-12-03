from openprocurement.tender.competitiveordering.procedure.state.tender import (
    OpenTenderState,
)
from openprocurement.tender.core.procedure.state.award_complaint import (
    AwardComplaintStateMixin,
)


class OpenAwardComplaintState(AwardComplaintStateMixin, OpenTenderState):
    pass
