from openprocurement.tender.core.procedure.serializers.base import BaseSerializer, ListSerializer


class ComplaintObjectionArgumentSerializer(BaseSerializer):
    serializers = {
        "evidences": ListSerializer(BaseSerializer),
    }
