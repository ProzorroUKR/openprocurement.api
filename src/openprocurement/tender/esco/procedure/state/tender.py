from openprocurement.tender.openeu.procedure.state.tender import BaseOpenEUTenderState
from openprocurement.tender.esco.procedure.models.award import Award
from openprocurement.tender.esco.procedure.models.contract import Contract


class ESCOTenderStateMixin:
    contract_model = Contract
    award_class = Award
    awarding_criteria_key: str = "amountPerformance"
    reverse_awarding_criteria: bool = True
    tender_weighted_value_pre_calculation: bool = False
    generate_award_milestones = False


class ESCOTenderTenderState(ESCOTenderStateMixin, BaseOpenEUTenderState):
    pass
