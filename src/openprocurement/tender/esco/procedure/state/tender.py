from openprocurement.tender.openeu.procedure.state.tender import BaseOpenEUTenderState
from openprocurement.tender.esco.procedure.models.award import Award
from openprocurement.tender.esco.procedure.models.contract import Contract


class ESCOTenderTenderState(BaseOpenEUTenderState):
    contract_model = Contract
    award_class = Award

    def calc_tender_values(self, tender: dict) -> None:
        if tender.get("lots"):
            self.calc_tender_guarantee(tender)
            self.calc_tender_min_value(tender)
            self.calc_tender_minimalStepPercentage(tender)
            self.calc_tender_yearlyPaymentsPercentageRange(tender)

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
    def calc_tender_minimalStepPercentage(tender: dict) -> None:
        if not tender.get("lots"):
            return
        tender["minimalStepPercentage"] = min(i["minimalStepPercentage"] for i in tender["lots"])

    @staticmethod
    def calc_tender_yearlyPaymentsPercentageRange(tender: dict) -> None:
        if not tender.get("lots"):
            return
        tender["yearlyPaymentsPercentageRange"] = min(i["yearlyPaymentsPercentageRange"] for i in tender["lots"])


