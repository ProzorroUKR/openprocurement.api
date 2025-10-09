from openprocurement.api.procedure.serializers.base import ListSerializer
from openprocurement.api.serializers_async.base import BaseSerializer
from openprocurement.api.serializers_async.document import DocumentSerializer


class ViolationReportDefendantStatementSerializer(BaseSerializer):
    serializers = {
        "documents": ListSerializer(DocumentSerializer),
    }
