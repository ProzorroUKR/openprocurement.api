from openprocurement.api.procedure.serializers.base import BaseUIDSerializer


class TransferredPlanSerializer(BaseUIDSerializer):
    public_fields = {
        "id",
        "owner",
    }
