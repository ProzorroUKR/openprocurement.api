from openprocurement.tender.core.procedure.serializers.base import BaseSerializer
from openprocurement.tender.esco.procedure.serializers.value import ValueSerializer


class LotValueSerializer(BaseSerializer):
    serializers = {
        "value": ValueSerializer,
    }
