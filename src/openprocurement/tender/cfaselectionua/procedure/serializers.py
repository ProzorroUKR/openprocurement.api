from openprocurement.api.procedure.serializers.base import ListSerializer
from openprocurement.tender.core.procedure.serializers.bid import (
    BidSerializer as BaseBidSerializer,
)
from openprocurement.tender.core.procedure.serializers.document import (
    DocumentSerializer,
)


def parameter_values_to_float(_, value):
    if isinstance(value, list):
        return [{"code": e["code"], "value": float(e["value"])} for e in value]
    return value


class BidSerializer(BaseBidSerializer):
    serializers = {
        "parameters": parameter_values_to_float,
        "documents": ListSerializer(DocumentSerializer),
        "eligibilityDocuments": ListSerializer(DocumentSerializer),
        "qualificationDocuments": ListSerializer(DocumentSerializer),
        "financialDocuments": ListSerializer(DocumentSerializer),
    }
