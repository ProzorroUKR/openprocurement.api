from openprocurement.tender.core.procedure.serializers.base import BaseUIDSerializer, ListSerializer
from openprocurement.tender.core.procedure.serializers.document import DocumentSerializer


class FrameworkSerializer(BaseUIDSerializer):
    base_private_fields = {
        "transfer_token",
        "_rev",
        "doc_type",
        "rev",
        "owner_token",
        "revisions",
        "public_modified",
        "is_public",
        "is_test",
        "config",
        "successful",
        "__parent__",
        "_attachments",
    }
    serializers = {
        "documents": ListSerializer(DocumentSerializer),
    }

    def __init__(self, data: dict):
        super().__init__(data)
        self.private_fields = set(self.base_private_fields)
