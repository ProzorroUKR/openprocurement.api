from openprocurement.api.procedure.serializers.base import BaseUIDSerializer


class TransferredPlanSerializer(BaseUIDSerializer):
    whitelist = {
        "_id",
        "owner",
    }
    serializers = {}
