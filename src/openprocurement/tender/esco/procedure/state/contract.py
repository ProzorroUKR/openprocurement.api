from decimal import Decimal

from openprocurement.api.procedure.utils import to_decimal
from openprocurement.api.utils import raise_operation_error
from openprocurement.tender.esco.procedure.state.tender import ESCOTenderState
from openprocurement.tender.openua.procedure.state.contract import (
    OpenUAContractStateMixing,
)


class ESCOContractStateMixing:
    value_attrs = (
        "amount",
        "amount_escp",
        "amountPerformance",
        "amountPerformance_npv",
        "yearlyPaymentsPercentage",
        "annualCostsReduction",
        "contractDuration",
        "currency",
    )

    @classmethod
    def validate_update_contract_value_esco(cls, request, before, after, convert_annual_costs=True):
        value = after.get("value")
        if value:
            for ro_attr in cls.value_attrs:
                field = before.get("value")
                if convert_annual_costs and ro_attr == "annualCostsReduction" and field.get(ro_attr):
                    # This made because of not everywhere DecimalType is new
                    # and when old model validate whole tender, value here become
                    # form 1E+2, but in request.validated['data'] we get '100'
                    field[ro_attr] = ['{:f}'.format(to_decimal(i)) for i in field[ro_attr]]
                if field:
                    passed = value.get(ro_attr)
                    actual = field.get(ro_attr)
                    if isinstance(passed, Decimal):
                        actual = to_decimal(actual)
                    if passed != actual:
                        raise_operation_error(request, f"Can't update {ro_attr} for contract value", name="value")


class ESCOContractState(OpenUAContractStateMixing, ESCOContractStateMixing, ESCOTenderState):
    def validate_contract_patch(self, request, before, after):
        super().validate_contract_patch(request, before, after)
        self.validate_update_contract_value_esco(request, before, after)
