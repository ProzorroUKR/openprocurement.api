from openprocurement.api.procedure.serializers.base import (
    BaseSerializer,
    ListSerializer,
)
from openprocurement.tender.core.procedure.serializers.complaint import (
    ComplaintSerializer,
)
from openprocurement.tender.core.procedure.serializers.document import (
    DocumentSerializer,
)
from openprocurement.tender.esco.procedure.serializers.value import ValueSerializer


class AwardSerializer(BaseSerializer):
    serializers = {
        "documents": ListSerializer(DocumentSerializer),
        "complaints": ListSerializer(ComplaintSerializer),
        "value": ValueSerializer,
        "weightedValue": ValueSerializer,
    }
