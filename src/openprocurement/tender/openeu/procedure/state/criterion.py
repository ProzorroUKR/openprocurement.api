from openprocurement.tender.core.procedure.state.criterion import CriterionStateMixin
from openprocurement.tender.openeu.procedure.state.tender import OpenEUTenderState


class OpenEUCriterionState(CriterionStateMixin, OpenEUTenderState):
    pass
