from openprocurement.tender.core.procedure.serializers.lot_value import (
    LotValueSerializer as BaseLotValueSerializer,
)
from openprocurement.tender.esco.procedure.serializers.value import ValueSerializer


class LotValueSerializer(BaseLotValueSerializer):
    serializers = {
        "value": ValueSerializer,
        "initialValue": ValueSerializer,
    }
