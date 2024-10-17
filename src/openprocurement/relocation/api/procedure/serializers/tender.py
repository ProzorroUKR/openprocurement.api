from openprocurement.api.procedure.serializers.base import BaseUIDSerializer


class TransferredTenderSerializer(BaseUIDSerializer):
    whitelist = {
        "id",
        "owner",
    }
    serializers = {}
