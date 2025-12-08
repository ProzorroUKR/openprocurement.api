from openprocurement.api.procedure.serializers.base import BaseUIDSerializer


class TransferredContractSerializer(BaseUIDSerializer):
    public_fields = {
        "id",
        "owner",
    }
