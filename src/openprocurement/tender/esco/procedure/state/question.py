from openprocurement.tender.core.procedure.state.question import TenderQuestionStateMixin
from openprocurement.tender.esco.procedure.state.tender import ESCOTenderState


class ESCOTenderQuestionState(TenderQuestionStateMixin, ESCOTenderState):
    pass
