from openprocurement.tender.core.procedure.serializers.base import ListSerializer
from openprocurement.tender.core.procedure.serializers.document import ConfidentialDocumentSerializer
from openprocurement.tender.core.procedure.serializers.parameter import ParameterSerializer
from openprocurement.tender.esco.procedure.serializers.lot_value import LotValueSerializer
from openprocurement.tender.esco.procedure.serializers.value import ValueSerializer
from openprocurement.tender.openeu.procedure.serializers.bid import BidSerializer as BaseBidSerializer


class BidSerializer(BaseBidSerializer):
    serializers = {
        "value": ValueSerializer,
        "lotValues": ListSerializer(LotValueSerializer),
        "documents": ListSerializer(ConfidentialDocumentSerializer),
        "parameters": ListSerializer(ParameterSerializer),
    }
