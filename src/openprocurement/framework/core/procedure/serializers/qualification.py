from openprocurement.api.constants import FRAMEWORK_CONFIG_JSONSCHEMAS
from openprocurement.api.context import get_request
from openprocurement.api.procedure.serializers.base import (
    BaseUIDSerializer,
    ListSerializer,
)
from openprocurement.api.procedure.serializers.config import (
    BaseConfigSerializer,
    none_is_false_serializer,
)
from openprocurement.api.utils import request_fetch_framework
from openprocurement.tender.core.procedure.serializers.document import (
    DocumentSerializer,
)


class QualificationSerializer(BaseUIDSerializer):
    base_private_fields = {
        "doc_type",
        "rev",
        "revisions",
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
    optional_fields = {
        "public_modified",
    }
    serializers = {
        "documents": ListSerializer(DocumentSerializer),
    }

    def __init__(self, data: dict):
        super().__init__(data)
        self.private_fields = set(self.base_private_fields)


def qualification_config_default_value(key):
    request = get_request()
    qualification = request.validated.get("qualification") or request.validated.get("data")
    request_fetch_framework(request, qualification.get("frameworkID"))
    framework = request.validated.get("framework")
    framework_type = framework.get("frameworkType")
    config_schema = FRAMEWORK_CONFIG_JSONSCHEMAS.get(framework_type)
    return config_schema["properties"][key]["default"]


def qualification_config_default_serializer(key):
    def serializer(value):
        if value is None:
            return qualification_config_default_value(key)
        return value

    return serializer


class QualificationConfigSerializer(BaseConfigSerializer):
    serializers = {
        "restricted": none_is_false_serializer,
        "qualificationComplainDuration": qualification_config_default_serializer("qualificationComplainDuration"),
    }
