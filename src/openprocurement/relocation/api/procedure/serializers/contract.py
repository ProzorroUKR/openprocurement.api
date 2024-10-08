from openprocurement.api.procedure.serializers.base import BaseUIDSerializer


class TransferredContractSerializer(BaseUIDSerializer):
    whitelist = {
        "id",
        "owner",
    }
    serializers = {}
