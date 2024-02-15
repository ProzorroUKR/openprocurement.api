from openprocurement.api.procedure.serializers.base import (
    BaseSerializer,
    ListSerializer,
)
from openprocurement.tender.core.procedure.serializers.complaint import (
    ComplaintSerializer,
)
from openprocurement.tender.core.procedure.serializers.document import (
    ConfidentialDocumentSerializer,
)


class AwardSerializer(BaseSerializer):
    serializers = {
        "documents": ListSerializer(ConfidentialDocumentSerializer),
        "complaints": ListSerializer(ComplaintSerializer),
    }
