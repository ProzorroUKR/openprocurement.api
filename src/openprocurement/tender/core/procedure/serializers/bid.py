from openprocurement.tender.core.procedure.serializers.base import BaseSerializer, ListSerializer
from openprocurement.tender.core.procedure.serializers.document import ConfidentialDocumentSerializer


def value_amount_to_float(_, value):
    if isinstance(value, dict) and "amount" in value:
        value["amount"] = float(value["amount"])
    return value


def lot_value_serializer(s, values):
    for item in values:
        if "value" in item:
            item["value"] = value_amount_to_float(s, item["value"])
    return values


class BidSerializer(BaseSerializer):
    serializers = {
        "value": value_amount_to_float,
        "lotValues": lot_value_serializer,
        "documents": ListSerializer(ConfidentialDocumentSerializer),
    }
    private_fields = {
        "owner",
        "owner_token",
        "transfer_token",
    }
