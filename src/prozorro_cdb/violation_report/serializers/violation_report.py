from prozorro_cdb.api.serializers.base import BaseSerializer, ListSerializer
from prozorro_cdb.api.serializers.organization import (
    BuyerSerializer,
    ProcuringEntitySerializer,
    SupplierSerializer,
)
from prozorro_cdb.violation_report.serializers.decision import (
    ViolationReportDecisionSerializer,
)
from prozorro_cdb.violation_report.serializers.defendant_statement import (
    ViolationReportDefendantStatementSerializer,
)
from prozorro_cdb.violation_report.serializers.violation_report_details import (
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
