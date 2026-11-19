from openprocurement.api.procedure.serializers.base import (
    BaseSerializer,
    ListSerializer,
)
from openprocurement.contracting.core.procedure.serializers.document import (
    ContractDocumentSerializer,
)


class TerminationDetailsSerializer(BaseSerializer):
    serializers = {
        "documents": ListSerializer(ContractDocumentSerializer),
    }
