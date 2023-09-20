from openprocurement.tender.core.procedure.serializers.base import BaseUIDSerializer


class TransferredTenderSerializer(BaseUIDSerializer):
    whitelist = {
        "_id",
        "owner",
    }
    serializers = {}
