from openprocurement.api.procedure.serializers.base import (
    BaseSerializer,
    ListSerializer,
)
from openprocurement.tender.core.procedure.serializers.complaint_objection_argument import (
    ComplaintObjectionArgumentSerializer,
)
from openprocurement.tender.core.procedure.serializers.complaint_objection_requested_remedy import (
    ComplaintRequestedRemedySerializer,
)


class ComplaintObjectionSerializer(BaseSerializer):
    serializers = {
        "arguments": ListSerializer(ComplaintObjectionArgumentSerializer),
        "requestedRemedies": ListSerializer(ComplaintRequestedRemedySerializer),
    }
