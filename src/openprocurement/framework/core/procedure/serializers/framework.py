from typing import Any

from openprocurement.api.procedure.serializers.base import (
    BaseUIDSerializer,
    ListSerializer,
)
from openprocurement.api.procedure.serializers.config import BaseConfigSerializer
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
        "public_modified",
        "public_ts",
        "is_public",
        "is_test",
        "config",
        "successful",
        "attachments",
    }
    serializers = {
        "documents": ListSerializer(DocumentSerializer),
        "questions": ListSerializer(QuestionSerializer),
    }

    def __init__(self, data: dict):
        super().__init__(data)
        self.private_fields = set(self.base_private_fields)

    def serialize(self, data: dict[str, Any], **kwargs) -> dict[str, Any]:
        kwargs["framework"] = self.raw
        return super().serialize(data, **kwargs)


def test_serializer(value):
    if value is False:
        return None
    return value


def restricted_derivatives_serializer(value):
    if value is None:
        return False
    return value


def clarification_until_duration_serializer(value):
    if value is None:
        return 3
    return value


def qualification_complain_duration_serializer(value):
    if value is None:
        return 0
    return value


class FrameworkConfigSerializer(BaseConfigSerializer):
    serializers = {
        "test": test_serializer,
        "restrictedDerivatives": restricted_derivatives_serializer,
        "clarificationUntilDuration": clarification_until_duration_serializer,
        "qualificationComplainDuration": qualification_complain_duration_serializer,
    }
