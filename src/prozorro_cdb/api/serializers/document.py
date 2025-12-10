from typing import Any

from prozorro_cdb.api.context import url_to_absolute
from prozorro_cdb.api.serializers.base import BaseSerializer, ListSerializer


class DocumentSerializer(BaseSerializer):
    serializers = {
        "url": url_to_absolute,
    }


class DocumentListSerializer(ListSerializer):
    def __call__(self, data: list[dict[str, Any]], **kwargs) -> ListSerializer:
        # remove old document versions from the list (with the same id)
        seen_ids = set()
        documents = []
        for d in reversed(data):
            if d["id"] not in seen_ids:
                seen_ids.add(d["id"])
                documents.append(d)
        return super().__call__(list(reversed(documents)), **kwargs)
