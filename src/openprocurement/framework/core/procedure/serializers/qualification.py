from openprocurement.api.procedure.serializers.base import ListSerializer, BaseUIDSerializer
from openprocurement.tender.core.procedure.serializers.document import DocumentSerializer


class QualificationSerializer(BaseUIDSerializer):
    base_private_fields = {
        "_rev",
        "doc_type",
        "rev",
        "revisions",
        "public_modified",
        "is_public",
        "is_test",
        "config",
        "__parent__",
        "_attachments",
        "dateCreated",
        "framework_owner",
        "framework_token",
        "submission_owner",
        "submission_token",
    }
    serializers = {
        "documents": ListSerializer(DocumentSerializer),
    }

    def __init__(self, data: dict):
        super().__init__(data)
        self.private_fields = set(self.base_private_fields)
