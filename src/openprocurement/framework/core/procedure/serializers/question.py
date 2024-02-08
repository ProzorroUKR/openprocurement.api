from hashlib import md5

from openprocurement.api.procedure.context import get_framework
from openprocurement.api.procedure.serializers.base import BaseSerializer


class AuthorSerializer(BaseSerializer):
    whitelist = {"identifier"}

    @property
    def data(self) -> dict:
        data = super().data
        identifier = data.pop("identifier")
        author_hash = f"{identifier['id']}_{get_framework()['owner_token']}"
        data["hash"] = md5(author_hash.encode("utf-8")).hexdigest()
        return data


class QuestionSerializer(BaseSerializer):
    serializers = {
        "author": AuthorSerializer,
    }
