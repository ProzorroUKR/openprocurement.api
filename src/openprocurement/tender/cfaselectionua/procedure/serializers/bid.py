from openprocurement.api.procedure.serializers.base import ListSerializer
from openprocurement.tender.cfaselectionua.procedure.serializers.parameter import (
    ParameterSerializer,
)
from openprocurement.tender.core.procedure.serializers.bid import (
    BidSerializer as BaseBidSerializer,
)
from openprocurement.tender.core.procedure.serializers.document import (
    DocumentSerializer,
)
from openprocurement.tender.core.procedure.serializers.lot_value import (
    LotValueSerializer,
)


class BidSerializer(BaseBidSerializer):
    serializers = {
        "parameters": ListSerializer(ParameterSerializer),
        "documents": ListSerializer(DocumentSerializer),
        "eligibilityDocuments": ListSerializer(DocumentSerializer),
        "qualificationDocuments": ListSerializer(DocumentSerializer),
        "financialDocuments": ListSerializer(DocumentSerializer),
        "lotValues": ListSerializer(LotValueSerializer),
    }
