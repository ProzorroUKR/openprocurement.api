from openprocurement.api.procedure.serializers.base import ListSerializer, BaseSerializer


class ComplaintObjectionArgumentSerializer(BaseSerializer):
    serializers = {
        "evidences": ListSerializer(BaseSerializer),
    }
