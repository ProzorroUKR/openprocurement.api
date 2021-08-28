from openprocurement.tender.core.procedure.serializers.base import ListSerializer
from openprocurement.tender.core.procedure.serializers.document import ConfidentialDocumentSerializer
from openprocurement.tender.core.procedure.serializers.bid import BidSerializer as BaseBidSerializer


def parameter_values_to_float(_, value):
    if isinstance(value, list):
        return [dict(code=e["code"], value=float(e["value"])) for e in value]
    return value


class BidSerializer(BaseBidSerializer):
    serializers = {
        "parameters": parameter_values_to_float,
        "documents": ListSerializer(ConfidentialDocumentSerializer),
    }
