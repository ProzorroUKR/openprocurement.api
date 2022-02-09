from openprocurement.tender.core.procedure.serializers.base import BaseSerializer


class ComplaintSerializer(BaseSerializer):
    private_fields = {
        "owner",
        "owner_token",
        "transfer_token",
    }
