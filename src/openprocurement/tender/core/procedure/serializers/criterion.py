from openprocurement.api.procedure.serializers.base import (
    BaseSerializer,
    ListSerializer,
)
from openprocurement.tender.core.procedure.serializers.criterion_rg import (
    RequirementGroupSerializer,
)


class CriterionSerializer(BaseSerializer):
    serializers = {
        "requirementGroups": ListSerializer(RequirementGroupSerializer),
    }
