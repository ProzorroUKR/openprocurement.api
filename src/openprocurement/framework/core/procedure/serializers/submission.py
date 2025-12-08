from openprocurement.api.procedure.serializers.base import (
    BaseUIDSerializer,
    ListSerializer,
)
from openprocurement.api.procedure.serializers.config import (
    BaseConfigSerializer,
    none_is_false_serializer,
)
from openprocurement.framework.core.procedure.serializers.document import (
    SubmissionDocumentSerializer,
)


class SubmissionSerializer(BaseUIDSerializer):
    base_private_fields = {
        "transfer_token",
        "doc_type",
        "rev",
        "revisions",
        "public_ts",
        "is_public",
        "is_test",
        "config",
        "attachments",
        "dateCreated",
        "owner_token",
        "framework_owner",
        "framework_token",
    }
    optional_fields = {
        "public_modified",
    }
    serializers = {
        "documents": ListSerializer(SubmissionDocumentSerializer),
    }

    def __init__(self, data: dict):
        super().__init__(data)
        self.private_fields = set(self.base_private_fields)


class SubmissionConfigSerializer(BaseConfigSerializer):
    serializers = {
        "restricted": none_is_false_serializer,
    }
