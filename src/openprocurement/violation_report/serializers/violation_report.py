from openprocurement.api.procedure.serializers.base import ListSerializer
from openprocurement.api.serializers_async.base import BaseSerializer
from openprocurement.api.serializers_async.document import DocumentSerializer
from openprocurement.violation_report.serializers.decision import (
    ViolationReportDecisionSerializer,
)
from openprocurement.violation_report.serializers.defendant_statement import (
    ViolationReportDefendantStatementSerializer,
)


class ViolationReportSerializer(BaseSerializer):
    serializers = {
        "documents": ListSerializer(DocumentSerializer),
        "decision": ViolationReportDecisionSerializer,
        "defendantStatement": ViolationReportDefendantStatementSerializer,
    }
