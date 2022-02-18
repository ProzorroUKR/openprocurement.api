from openprocurement.tender.core.procedure.serializers.base import BaseSerializer, decimal_serializer


class LotSerializer(BaseSerializer):
    serializers = {
        "yearlyPaymentsPercentageRange": decimal_serializer,
        "minimalStepPercentage": decimal_serializer,
    }
