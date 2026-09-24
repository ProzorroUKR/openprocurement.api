from openprocurement.api.auth import AccreditationLevel
from openprocurement.tender.core.procedure.state.question import (
    TenderQuestionStateMixin,
)
from openprocurement.tender.open.procedure.state.tender import (
    AboveThresholdEUTenderState,
    AboveThresholdTenderState,
    AboveThresholdUATenderState,
    BelowThresholdTenderState,
    COTenderState,
    DefenseTenderState,
    RFPTenderState,
)


class AboveThresholdTenderQuestionStateMixin(TenderQuestionStateMixin):
    question_create_accreditations = None


class AboveThresholdTenderQuestionState(AboveThresholdTenderQuestionStateMixin, AboveThresholdTenderState):
    question_create_accreditations = (AccreditationLevel.ACCR_4,)


class AboveThresholdUATenderQuestionStateMixin(TenderQuestionStateMixin):
    question_create_accreditations = None


class AboveThresholdUATenderQuestionState(AboveThresholdUATenderQuestionStateMixin, AboveThresholdUATenderState):
    question_create_accreditations = (AccreditationLevel.ACCR_4,)


class AboveThresholdEUTenderQuestionState(TenderQuestionStateMixin, AboveThresholdEUTenderState):
    pass


class DefenseTenderQuestionState(TenderQuestionStateMixin, DefenseTenderState):
    pass


class COTenderQuestionStateMixin(TenderQuestionStateMixin):
    question_create_accreditations = None


class COTenderQuestionState(COTenderQuestionStateMixin, COTenderState):
    question_create_accreditations = (AccreditationLevel.ACCR_4,)


class BelowThresholdTenderQuestionState(TenderQuestionStateMixin, BelowThresholdTenderState):
    question_create_accreditations = (AccreditationLevel.ACCR_2,)

    question_operation_allowed_tender_statuses = None


class RFPTenderQuestionState(TenderQuestionStateMixin, RFPTenderState):
    question_create_accreditations = (AccreditationLevel.ACCR_2,)

    question_operation_allowed_tender_statuses = None
