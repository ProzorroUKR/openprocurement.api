from prozorro_cdb.api.serializers.base import BaseSerializer
from prozorro_cdb.api.serializers.document import (
    DocumentListSerializer,
    DocumentSerializer,
)


class ViolationReportDefendantStatementSerializer(BaseSerializer):
    serializers = {
        "documents": DocumentListSerializer(DocumentSerializer),
    }
