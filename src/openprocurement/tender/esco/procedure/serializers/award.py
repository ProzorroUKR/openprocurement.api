from openprocurement.tender.core.procedure.serializers.base import BaseSerializer, ListSerializer
from openprocurement.tender.core.procedure.serializers.document import ConfidentialDocumentSerializer
from openprocurement.tender.core.procedure.serializers.complaint import ComplaintSerializer
from openprocurement.tender.esco.procedure.serializers.value import ValueSerializer


class AwardSerializer(BaseSerializer):
    serializers = {
        "documents": ListSerializer(ConfidentialDocumentSerializer),
        "complaints": ListSerializer(ComplaintSerializer),
        "value": ValueSerializer,
        "weightedValue": ValueSerializer,
    }
