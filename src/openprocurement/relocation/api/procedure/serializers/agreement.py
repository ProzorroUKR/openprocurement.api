from openprocurement.api.procedure.serializers.base import BaseUIDSerializer


class TransferredAgreementSerializer(BaseUIDSerializer):
    whitelist = {
        "id",
        "owner",
    }
    serializers = {}
