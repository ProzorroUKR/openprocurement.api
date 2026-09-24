from openprocurement.api.auth import AccreditationLevel
from openprocurement.tender.competitivedialogue.procedure.state.stage1.tender_details import (
    CDStage1TenderDetailsStateMixin,
)
from openprocurement.tender.core.procedure.state.question import TenderQuestionStateMixin


class CDStage1TenderQuestionState(TenderQuestionStateMixin, CDStage1TenderDetailsStateMixin):
    question_create_accreditations = (AccreditationLevel.ACCR_4,)

    question_operation_allowed_tender_statuses = ("active.tendering",)
