from openprocurement.api.procedure.serializers.base import BaseSerializer
from openprocurement.api.procedure.serializers.document import download_url_serialize


class DocumentSerializer(BaseSerializer):
    serializers = {
        "url": download_url_serialize,
    }
