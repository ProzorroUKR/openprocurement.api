from openprocurement.api.context_async import url_to_absolute
from openprocurement.api.serializers_async.base import BaseSerializer


class DocumentSerializer(BaseSerializer):
    serializers = {
        "url": url_to_absolute,
    }
