from openprocurement.api.procedure.serializers.base import (
    BaseUIDSerializer,
    ListSerializer,
)
from openprocurement.api.procedure.serializers.config import BaseConfigSerializer
from openprocurement.framework.core.procedure.serializers.framework import (
    qualification_complain_duration_serializer,
)
from openprocurement.tender.core.procedure.serializers.document import (
    DocumentSerializer,
)


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


def test_serializer(obj, value):
    if value is False:
        return None
    return value


def restricted_serializer(obj, value):
    if value is None:
        return False
    return value


class QualificationConfigSerializer(BaseConfigSerializer):
    serializers = {
        "test": test_serializer,
        "restricted": restricted_serializer,
        "qualificationComplainDuration": qualification_complain_duration_serializer,
    }
