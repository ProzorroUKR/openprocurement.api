from openprocurement.api.auth import ACCR_2
from openprocurement.tender.belowthreshold.procedure.state.tender import (
    BelowThresholdTenderState,
)
from openprocurement.tender.core.procedure.state.question import (
    TenderQuestionStateMixin,
)


class BelowThresholdTenderQuestionState(TenderQuestionStateMixin, BelowThresholdTenderState):
    question_create_accreditations = (ACCR_2,)
