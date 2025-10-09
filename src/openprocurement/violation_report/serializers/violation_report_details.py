from openprocurement.api.procedure.serializers.base import ListSerializer
from openprocurement.api.serializers_async.base import BaseSerializer
from openprocurement.api.serializers_async.document import DocumentSerializer


class ViolationReportDetailsSerializer(BaseSerializer):
    serializers = {
        "documents": ListSerializer(DocumentSerializer),
    }
