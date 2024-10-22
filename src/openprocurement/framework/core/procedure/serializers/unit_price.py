from openprocurement.api.procedure.serializers.base import BaseSerializer
from openprocurement.framework.core.procedure.serializers.value import ValueSerializer


class UnitPriceSerializer(BaseSerializer):
    serializers = {
        "value": ValueSerializer,
    }
