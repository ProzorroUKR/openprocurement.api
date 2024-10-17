from openprocurement.api.procedure.serializers.base import (
    BaseSerializer,
    ListSerializer,
)
from openprocurement.tender.core.procedure.serializers.criterion_rg_requirement_evidence import (
    EligibleEvidenceSerializer,
)


class RequirementSerializer(BaseSerializer):
    serializers = {
        "eligibleEvidences": ListSerializer(EligibleEvidenceSerializer),
    }


class PutCancelledRequirementSerializer(RequirementSerializer):
    whitelist = [
        "id",
        "status",
        "datePublished",
        "dateModified",
    ]
