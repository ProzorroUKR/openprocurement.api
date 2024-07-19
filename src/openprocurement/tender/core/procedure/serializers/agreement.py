from openprocurement.api.procedure.serializers.base import (
    BaseSerializer,
    ListSerializer,
)
from openprocurement.tender.core.procedure.serializers.document import (
    DocumentSerializer,
)


class AgreementSerializer(BaseSerializer):
    serializers = {
        "documents": ListSerializer(DocumentSerializer),
    }
