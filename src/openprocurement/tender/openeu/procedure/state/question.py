from openprocurement.tender.core.procedure.state.question import TenderQuestionStateMixin
from openprocurement.tender.openeu.procedure.state.tender import OpenEUTenderState


class OpenEUTenderQuestionState(TenderQuestionStateMixin, OpenEUTenderState):
    pass
