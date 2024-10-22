from openprocurement.api.procedure.serializers.base import (
    BaseSerializer,
    ListSerializer,
)
from openprocurement.framework.core.procedure.serializers.milestone import (
    MilestoneSerializer,
)
from openprocurement.framework.core.procedure.serializers.unit_price import (
    UnitPriceSerializer,
)


class ContractSerializer(BaseSerializer):
    base_private_fields = {
        "doc_type",
        "rev",
    }

    serializers = {
        "unitPrices": ListSerializer(UnitPriceSerializer),
        "milestones": ListSerializer(MilestoneSerializer),
    }

    def __init__(self, data: dict):
        super().__init__(data)
        self.private_fields = set(self.base_private_fields)
