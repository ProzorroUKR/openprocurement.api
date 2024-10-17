from openprocurement.api.procedure.serializers.base import BaseSerializer


class ParameterSerializer(BaseSerializer):
    serializers = {
        "value": float,
    }
