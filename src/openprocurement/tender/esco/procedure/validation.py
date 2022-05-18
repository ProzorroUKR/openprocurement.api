from openprocurement.api.utils import raise_operation_error, to_decimal
from decimal import Decimal


def validate_update_contract_value_esco(request, **_):
    data = request.validated["data"]
    value = data.get("value")
    attrs = (
        "amount",
        "amount_escp",
        "amountPerformance",
        "amountPerformance_npv",
        "yearlyPaymentsPercentage",
        "annualCostsReduction",
        "contractDuration",
        "currency",
    )
    if value:
        for ro_attr in attrs:
            field = request.validated["contract"].get("value")
            if ro_attr == "annualCostsReduction" and field.get(ro_attr):
                # This made because of not everywhere DecimalType is new
                # and when old model validate whole tender, value here become
                # form 1E+2, but in request.validated['data'] we get '100'
                field[ro_attr] = ['{0:f}'.format(to_decimal(i)) for i in field[ro_attr]]
            if field:
                passed = value.get(ro_attr)
                actual = field.get(ro_attr)
                # TODO: we are getting Decimal from db now, so we don't have to convert DecimalType to str
                #  which I believe a cause of this
                if isinstance(actual, Decimal) and passed:
                    passed = Decimal(passed)
                if passed != actual:
                    raise_operation_error(request, f"Can't update {ro_attr} for contract value", name="value")
