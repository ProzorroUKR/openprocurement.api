from openprocurement.tender.core.procedure.serializers.base import BaseUIDSerializer


class TransferredPlanSerializer(BaseUIDSerializer):
    whitelist = {
        "_id",
        "owner",
    }
    serializers = {}
