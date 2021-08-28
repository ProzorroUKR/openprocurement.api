from openprocurement.tender.core.procedure.serializers.base import ListSerializer
from openprocurement.tender.core.procedure.serializers.document import ConfidentialDocumentSerializer
from openprocurement.tender.openeu.procedure.serializers import BidSerializer as BaseBidSerializer


def bid_value_to_float(_, value):
    costs_reduction = value.get("annualCostsReduction")
    if isinstance(costs_reduction, list):
        value["annualCostsReduction"] = tuple(float(e) for e in costs_reduction)

    yearly_percentage = value.get("yearlyPaymentsPercentage")
    if yearly_percentage:
        value["yearlyPaymentsPercentage"] = float(yearly_percentage)

    amount = value.get("amount")
    if amount:
        value["amount"] = float(amount)

    amount_performance = value.get("amountPerformance")
    if amount_performance:
        value["amountPerformance"] = float(amount_performance)

    return value


def bid_lot_values_to_float(s, lot_values):
    if isinstance(lot_values, list):
        for lot_value in lot_values:
            lot_value["value"] = bid_value_to_float(s, lot_value["value"])
    return lot_values


class BidSerializer(BaseBidSerializer):
    serializers = {
        "value": bid_value_to_float,
        "lotValues": bid_lot_values_to_float,
        "documents": ListSerializer(ConfidentialDocumentSerializer),
    }
