from openprocurement.api.procedure.serializers.base import BaseSerializer


class MilestoneSerializer(BaseSerializer):
    base_private_fields = {
        "owner_token",
    }
    serializers = {}

    def __init__(self, data: dict):
        super().__init__(data)
        self.private_fields = set(self.base_private_fields)
