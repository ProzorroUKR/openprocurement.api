from openprocurement.api.procedure.serializers.base import ListSerializer, BaseSerializer, decimal_serializer


class ValueSerializer(BaseSerializer):
    serializers = {
        "annualCostsReduction": ListSerializer(decimal_serializer),
        "yearlyPaymentsPercentage": decimal_serializer,
        "amount": decimal_serializer,
        "amountPerformance": decimal_serializer,
        "denominator": decimal_serializer,
        "addition": decimal_serializer,
    }
