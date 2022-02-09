from openprocurement.tender.core.procedure.serializers.base import BaseSerializer, decimal_serializer


class GuaranteeSerializer(BaseSerializer):
    serializers = {
        "amount": decimal_serializer,
    }

