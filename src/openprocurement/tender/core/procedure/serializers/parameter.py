from openprocurement.api.procedure.serializers.base import (
    BaseSerializer,
    decimal_serializer,
)


class ParameterSerializer(BaseSerializer):
    serializers = {
        "value": decimal_serializer,
    }
