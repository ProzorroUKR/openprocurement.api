from openprocurement.api.procedure.serializers.base import BaseUIDSerializer


class TransferSerializer(BaseUIDSerializer):
    public_fields = {
        "id",
        "date",
        "usedFor",
    }
