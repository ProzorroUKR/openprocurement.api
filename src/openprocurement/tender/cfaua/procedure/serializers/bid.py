from openprocurement.api.procedure.serializers.base import ListSerializer
from openprocurement.tender.cfaua.procedure.serializers.lot_value import (
    LotValueSerializer,
)
from openprocurement.tender.cfaua.procedure.serializers.value import ValueSerializer
from openprocurement.tender.core.procedure.serializers.bid import (
    BidSerializer as BaseBidSerializer,
)
from openprocurement.tender.core.procedure.serializers.document import (
    DocumentSerializer,
)
from openprocurement.tender.core.procedure.serializers.req_response import (
    RequirementResponseSerializer,
)


class BidSerializer(BaseBidSerializer):
    serializers = {
        "documents": ListSerializer(DocumentSerializer),
        "eligibilityDocuments": ListSerializer(DocumentSerializer),
        "qualificationDocuments": ListSerializer(DocumentSerializer),
        "financialDocuments": ListSerializer(DocumentSerializer),
        "value": ValueSerializer,
        "initialValue": ValueSerializer,
        "lotValues": ListSerializer(LotValueSerializer),
        "requirementResponses": ListSerializer(RequirementResponseSerializer),
    }
