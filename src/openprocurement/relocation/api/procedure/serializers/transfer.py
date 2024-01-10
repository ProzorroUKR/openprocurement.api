from openprocurement.api.procedure.serializers.base import BaseUIDSerializer


class TransferSerializer(BaseUIDSerializer):
    whitelist = {
        "_id",
        "date",
        "usedFor",
    }
    serializers = {}
