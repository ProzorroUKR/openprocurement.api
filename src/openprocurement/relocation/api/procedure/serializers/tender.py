from openprocurement.api.procedure.serializers.base import BaseUIDSerializer


class TransferredTenderSerializer(BaseUIDSerializer):
    public_fields = {
        "id",
        "owner",
    }
