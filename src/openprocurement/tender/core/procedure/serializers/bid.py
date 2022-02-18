from openprocurement.tender.core.procedure.serializers.base import BaseSerializer, ListSerializer
from openprocurement.tender.core.procedure.serializers.document import ConfidentialDocumentSerializer


class BidSerializer(BaseSerializer):
    serializers = {
        "documents": ListSerializer(ConfidentialDocumentSerializer),
    }
    private_fields = {
        "owner",
        "owner_token",
        "transfer_token",
    }

    def __init__(self, data: dict):
        super().__init__(data)
        if data.get("status") in ("invalid", "deleted"):
            self.whitelist = {"id", "status"}

