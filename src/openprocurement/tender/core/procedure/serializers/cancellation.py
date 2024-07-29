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


class CancellationSerializer(BaseSerializer):
    serializers = {
        "complaints": ListSerializer(ComplaintSerializer),
        "documents": ListSerializer(DocumentSerializer),
    }
