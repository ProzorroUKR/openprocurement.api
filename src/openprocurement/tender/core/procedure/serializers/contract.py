from openprocurement.api.procedure.serializers.base import ListSerializer, BaseSerializer
from openprocurement.tender.core.procedure.serializers.document import ConfidentialDocumentSerializer


class ContractSerializer(BaseSerializer):
    serializers = {
        "documents": ListSerializer(ConfidentialDocumentSerializer),
    }
    private_fields = {
        "owner",
        "owner_token",
        "transfer_token",
    }
