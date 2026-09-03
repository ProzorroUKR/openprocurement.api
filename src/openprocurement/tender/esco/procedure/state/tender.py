from openprocurement.tender.core.procedure.models.award import ESCOAward as Award
from openprocurement.tender.openeu.procedure.state.tender import BaseOpenEUTenderState


class ESCOTenderStateMixin:
    award_class = Award
    awarding_criteria_key: str = "amountPerformance"
    reverse_awarding_criteria: bool = True
    tender_weighted_value_pre_calculation: bool = False
    generate_award_milestones = False


class ESCOTenderState(ESCOTenderStateMixin, BaseOpenEUTenderState):
    pass
