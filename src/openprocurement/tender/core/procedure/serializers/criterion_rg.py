from openprocurement.api.procedure.serializers.base import (
    BaseSerializer,
    ListSerializer,
)
from openprocurement.tender.core.procedure.serializers.criterion_rg_requirement import (
    RequirementSerializer,
)


class RequirementGroupSerializer(BaseSerializer):
    serializers = {
        "requirements": ListSerializer(RequirementSerializer),
    }
