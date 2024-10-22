from openprocurement.api.procedure.serializers.base import BaseSerializer
from openprocurement.api.procedure.utils import to_decimal


class ValueSerializer(BaseSerializer):
    serializers = {
        "amount": to_decimal,
    }
