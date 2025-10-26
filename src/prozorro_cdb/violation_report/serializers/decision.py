from prozorro_cdb.api.serializers.base import BaseSerializer, ListSerializer
from prozorro_cdb.api.serializers.document import DocumentSerializer


class ViolationReportDecisionSerializer(BaseSerializer):
    serializers = {
        "documents": ListSerializer(DocumentSerializer),
    }
