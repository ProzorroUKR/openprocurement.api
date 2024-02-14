from openprocurement.api.procedure.context import get_tender
from openprocurement.api.procedure.serializers.author import (
    HiddenAuthorSerializer as BaseHiddenAuthorSerializer,
)
from openprocurement.api.procedure.serializers.base import BaseSerializer


class HiddenAuthorSerializer(BaseHiddenAuthorSerializer):

    @property
    def data(self) -> dict:
        self._data["hash"] = self.get_hash(get_tender()['owner_token'])
        return super().data


class QuestionSerializer(BaseSerializer):
    serializers = {
        "author": HiddenAuthorSerializer,
    }
