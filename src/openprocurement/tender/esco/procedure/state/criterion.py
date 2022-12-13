from openprocurement.tender.core.procedure.state.criterion import CriterionStateMixin
from openprocurement.tender.esco.procedure.state.tender import ESCOTenderTenderState


class ESCOCriterionState(CriterionStateMixin, ESCOTenderTenderState):
    pass
