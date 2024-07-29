from openprocurement.api.procedure.serializers.base import (
    BaseSerializer,
    ListSerializer,
)
from openprocurement.tender.core.procedure.serializers.document import (
    DocumentSerializer,
)


class ContractSerializer(BaseSerializer):
    serializers = {
        "documents": ListSerializer(DocumentSerializer),
    }
    private_fields = {
        "owner",
        "owner_token",
        "transfer_token",
    }
