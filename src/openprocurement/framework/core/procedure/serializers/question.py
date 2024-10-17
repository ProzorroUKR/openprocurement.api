from typing import Any

from openprocurement.api.procedure.serializers.author import (
    HiddenAuthorSerializer as BaseHiddenAuthorSerializer,
)
from openprocurement.api.procedure.serializers.base import BaseSerializer


class HiddenAuthorSerializer(BaseHiddenAuthorSerializer):
    def serialize(self, data: dict[str, Any], framework=None, **kwargs) -> dict[str, Any]:
        data = data.copy()
        data["hash"] = self.get_hash(framework["owner_token"])
        return super().serialize(data, **kwargs)


class QuestionSerializer(BaseSerializer):
    serializers = {
        "author": HiddenAuthorSerializer,
    }
