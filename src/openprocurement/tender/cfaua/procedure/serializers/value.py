from openprocurement.api.procedure.serializers.base import BaseSerializer


class ValueSerializer(BaseSerializer):
    serializers = {
        "amount": float,
    }
