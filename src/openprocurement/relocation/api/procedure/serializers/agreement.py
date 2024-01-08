from openprocurement.tender.core.procedure.serializers.base import BaseUIDSerializer


class TransferredAgreementSerializer(BaseUIDSerializer):
    whitelist = {
        "_id",
        "owner",
    }
    serializers = {}
