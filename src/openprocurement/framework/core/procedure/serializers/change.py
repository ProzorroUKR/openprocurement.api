from openprocurement.api.procedure.serializers.base import (
    BaseSerializer,
    ListSerializer,
)
from openprocurement.tender.core.procedure.serializers.document import (
    DocumentSerializer,
)


class ChangeSerializer(BaseSerializer):
    serializers = {
        "documents": ListSerializer(DocumentSerializer),
    }
