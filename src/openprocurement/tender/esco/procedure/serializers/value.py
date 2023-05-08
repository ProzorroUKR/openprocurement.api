from openprocurement.tender.core.procedure.serializers.base import BaseSerializer, ListSerializer, decimal_serializer


class ValueSerializer(BaseSerializer):
    serializers = {
        "annualCostsReduction": ListSerializer(decimal_serializer),
        "yearlyPaymentsPercentage": decimal_serializer,
        "amount": decimal_serializer,
        "amountPerformance": decimal_serializer,
        "denominator": decimal_serializer,
        "addition": decimal_serializer,
    }
