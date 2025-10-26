from prozorro_cdb.api.context import url_to_absolute
from prozorro_cdb.api.serializers.base import BaseSerializer


class DocumentSerializer(BaseSerializer):
    serializers = {
        "url": url_to_absolute,
    }
