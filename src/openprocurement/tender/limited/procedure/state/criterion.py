from openprocurement.tender.core.procedure.state.criterion import CriterionStateMixin
from openprocurement.tender.core.procedure.state.tender import TenderState


class LimitedCriterionState(CriterionStateMixin, TenderState):
    criterion_source_choices = ("procuringEntity",)
