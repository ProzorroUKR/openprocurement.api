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
from openprocurement.tender.core.procedure.serializers.req_response import (
    RequirementResponseSerializer,
)


class QualificationSerializer(BaseSerializer):
    serializers = {
        "complaints": ListSerializer(ComplaintSerializer),
        "documents": ListSerializer(DocumentSerializer),
        "requirementResponses": ListSerializer(RequirementResponseSerializer),
    }
