from openprocurement.api.utils import raise_operation_error
from openprocurement.tender.core.procedure.context import get_tender_config
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

    def validate_minimal_step(self, data):
        config = get_tender_config()
        minimal_step_fields = ("minimalStepPercentage", "yearlyPaymentsPercentageRange")
        for field in minimal_step_fields:
            if config.get("hasAuction") is True and data.get(field) is None:
                raise_operation_error(
                    self.request,
                    ["This field is required."],
                    status=422,
                    location="body",
                    name=field,
                )
            elif config.get("hasAuction") is False and data.get(field) is not None:
                raise_operation_error(
                    self.request,
                    ["This field is not allowed."],
                    status=422,
                    location="body",
                    name=field,
                )


class ESCOTenderTenderState(ESCOTenderStateMixin, BaseOpenEUTenderState):
    contract_model = Contract
    award_class = Award
