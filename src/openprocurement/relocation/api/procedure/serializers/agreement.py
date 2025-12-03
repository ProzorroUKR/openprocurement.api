from openprocurement.api.procedure.serializers.base import BaseUIDSerializer


class TransferredAgreementSerializer(BaseUIDSerializer):
    public_fields = {
        "id",
        "owner",
    }
