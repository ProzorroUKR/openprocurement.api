from openprocurement.tender.openeu.procedure.state.tender import BaseOpenEUTenderState
from openprocurement.tender.esco.procedure.models.award import Award
from openprocurement.tender.esco.procedure.models.contract import Contract


class ESCOTenderStateMixin:
    def calc_tender_values(self, tender: dict) -> None:
        self.calc_tender_guarantee(tender)
        self.calc_tender_min_value(tender)
        self.calc_tender_minimal_step_percentage(tender)
        self.calc_tender_yearly_payments_percentage_range(tender)

    @staticmethod
    def calc_tender_min_value(tender: dict) -> None:
        if not tender.get("lots"):
            return
        tender["minValue"] = {
            "amount": sum(i["minValue"]["amount"] for i in tender["lots"] if i.get("minValue")),
            "currency": tender["minValue"]["currency"],
            "valueAddedTaxIncluded": tender["minValue"]["valueAddedTaxIncluded"]
        }

    @staticmethod
    def calc_tender_minimal_step_percentage(tender: dict) -> None:
        if not tender.get("lots"):
            return
        tender["minimalStepPercentage"] = min(i["minimalStepPercentage"] for i in tender["lots"])

    @staticmethod
    def calc_tender_yearly_payments_percentage_range(tender: dict) -> None:
        if not tender.get("lots"):
            return
        tender["yearlyPaymentsPercentageRange"] = min(i["yearlyPaymentsPercentageRange"] for i in tender["lots"])


class ESCOTenderTenderState(ESCOTenderStateMixin, BaseOpenEUTenderState):
    contract_model = Contract
    award_class = Award
    awarding_criteria_key: str = "amountPerformance"
    reverse_awarding_criteria: bool = True
    tender_weighted_value_pre_calculation: bool = False
    generate_award_milestones = False
