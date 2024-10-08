from openprocurement.tender.cfaua.procedure.serializers.value import ValueSerializer
from openprocurement.tender.core.procedure.serializers.lot_value import (
    LotValueSerializer as BaseLotValueSerializer,
)


class LotValueSerializer(BaseLotValueSerializer):
    serializers = {
        "value": ValueSerializer,
    }
