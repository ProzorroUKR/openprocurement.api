from openprocurement.api.procedure.serializers.base import (
    BaseSerializer,
    ListSerializer,
)


class ComplaintObjectionArgumentSerializer(BaseSerializer):
    serializers = {
        "evidences": ListSerializer(BaseSerializer),
    }
