from openprocurement.api.procedure.serializers.base import BaseUIDSerializer


class TransferSerializer(BaseUIDSerializer):
    whitelist = {
        "id",
        "date",
        "usedFor",
    }
    serializers = {}
