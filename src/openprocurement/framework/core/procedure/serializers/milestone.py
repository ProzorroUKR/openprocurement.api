from openprocurement.api.procedure.serializers.base import ListSerializer, BaseSerializer
from openprocurement.tender.core.procedure.serializers.document import DocumentSerializer


class MilestoneSerializer(BaseSerializer):
    base_private_fields = {
        "_rev",
        "doc_type",
        "rev",
        "__parent__",
    }

    serializers = {
        "documents": ListSerializer(DocumentSerializer),
    }

    def __init__(self, data: dict):
        super().__init__(data)
        self.private_fields = set(self.base_private_fields)
