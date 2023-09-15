from openprocurement.framework.core.procedure.serializers.milestone import MilestoneSerializer
from openprocurement.tender.core.procedure.serializers.base import BaseSerializer, ListSerializer


class ContractSerializer(BaseSerializer):
    base_private_fields = {
        "_rev",
        "doc_type",
        "rev",
        "__parent__",
    }

    serializers = {
        "milestones": ListSerializer(MilestoneSerializer),
    }

    def __init__(self, data: dict):
        super().__init__(data)
        self.private_fields = set(self.base_private_fields)
