from openprocurement.tender.core.procedure.serializers.base import BaseSerializer, ListSerializer
from openprocurement.tender.core.procedure.serializers.complaint import ComplaintSerializer


class QualificationSerializer(BaseSerializer):
    serializers = {
        "complaints": ListSerializer(ComplaintSerializer),
    }
