from openprocurement.api.procedure.serializers.base import (
    BaseUIDSerializer,
    ListSerializer,
)
from openprocurement.api.procedure.serializers.config import (
    BaseConfigSerializer,
    false_is_none_serializer,
    none_is_false_serializer,
)
from openprocurement.framework.core.procedure.serializers.framework import (
    framework_config_default_serializer,
)
from openprocurement.tender.core.procedure.serializers.document import (
    DocumentSerializer,
)


class QualificationSerializer(BaseUIDSerializer):
    base_private_fields = {
        "doc_type",
        "rev",
        "revisions",
        "public_modified",
        "public_ts",
        "is_public",
        "is_test",
        "config",
        "attachments",
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


class QualificationConfigSerializer(BaseConfigSerializer):
    serializers = {
        "test": false_is_none_serializer,
        "restricted": none_is_false_serializer,
        "qualificationComplainDuration": framework_config_default_serializer("qualificationComplainDuration"),
    }
