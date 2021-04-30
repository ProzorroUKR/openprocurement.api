from openprocurement.tender.core.procedure.serializers import (
    BidSerializer as BaseBidSerializer,
    lot_value_serializer,
    value_amount_to_float,
)


def parameter_values_to_float(_, value):
    if isinstance(value, list):
        return [dict(code=e["code"], value=float(e["value"])) for e in value]
    return value


class BidSerializer(BaseBidSerializer):
    serializers = {
        "value": value_amount_to_float,
        "lotValues": lot_value_serializer,
        "parameters": parameter_values_to_float,
    }
