from typing import Any

from openprocurement.api.constants import FRAMEWORK_CONFIG_JSONSCHEMAS
from openprocurement.api.context import get_request
from openprocurement.api.procedure.serializers.base import (
    BaseUIDSerializer,
    ListSerializer,
)
from openprocurement.api.procedure.serializers.config import BaseConfigSerializer
from openprocurement.framework.core.procedure.serializers.change import ChangeSerializer
from openprocurement.framework.core.procedure.serializers.question import (
    QuestionSerializer,
)
from openprocurement.tender.core.procedure.serializers.document import (
    DocumentSerializer,
)


class FrameworkSerializer(BaseUIDSerializer):
    base_private_fields = {
        "transfer_token",
        "doc_type",
        "rev",
        "owner_token",
        "revisions",
        "public_ts",
        "is_public",
        "is_test",
        "config",
        "successful",
        "attachments",
    }
    optional_fields = {
        "public_modified",
    }
    serializers = {
        "documents": ListSerializer(DocumentSerializer),
        "questions": ListSerializer(QuestionSerializer),
        "changes": ListSerializer(ChangeSerializer),
    }

    def __init__(self, data: dict):
        super().__init__(data)
        self.private_fields = set(self.base_private_fields)

    def serialize(self, data: dict[str, Any], **kwargs) -> dict[str, Any]:
        kwargs["framework"] = self.raw
        return super().serialize(data, **kwargs)


def framework_config_default_value(key):
    request = get_request()
    framework = request.validated.get("framework") or request.validated.get("data")
    framework_type = framework.get("frameworkType")
    config_schema = FRAMEWORK_CONFIG_JSONSCHEMAS.get(framework_type)
    return config_schema["properties"][key]["default"]


def framework_config_default_serializer(key):
    def serializer(value):
        if value is None:
            return framework_config_default_value(key)
        return value

    return serializer


class FrameworkConfigSerializer(BaseConfigSerializer):
    serializers = {
        "restrictedDerivatives": framework_config_default_serializer("restrictedDerivatives"),
        "clarificationUntilDuration": framework_config_default_serializer("clarificationUntilDuration"),
        "qualificationComplainDuration": framework_config_default_serializer("qualificationComplainDuration"),
        "hasItems": framework_config_default_serializer("hasItems"),
    }
