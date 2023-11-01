from openprocurement.tender.core.procedure.state.criterion import CriterionStateMixin
from openprocurement.tender.esco.procedure.state.tender import ESCOTenderState


class ESCOCriterionState(CriterionStateMixin, ESCOTenderState):
    pass
