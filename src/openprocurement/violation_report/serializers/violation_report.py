from openprocurement.api.procedure.serializers.base import ListSerializer
from openprocurement.api.serializers_async.base import BaseSerializer
from openprocurement.api.serializers_async.organization import (
    BuyerSerializer,
    ProcuringEntitySerializer,
    SupplierSerializer,
)
from openprocurement.violation_report.serializers.decision import (
    ViolationReportDecisionSerializer,
)
from openprocurement.violation_report.serializers.defendant_statement import (
    ViolationReportDefendantStatementSerializer,
)
from openprocurement.violation_report.serializers.violation_report_details import (
    ViolationReportDetailsSerializer,
)


class ViolationReportSerializer(BaseSerializer):
    private_fields = ["rev"]
    serializers = {
        "details": ViolationReportDetailsSerializer,
        "decision": ViolationReportDecisionSerializer,
        "defendantStatement": ViolationReportDefendantStatementSerializer,
        "author": BuyerSerializer,
        "defendants": ListSerializer(SupplierSerializer),
        "authority": ProcuringEntitySerializer,
    }
