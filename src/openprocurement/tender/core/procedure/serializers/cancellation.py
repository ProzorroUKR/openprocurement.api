from openprocurement.api.procedure.serializers.base import ListSerializer, BaseSerializer
from openprocurement.tender.core.procedure.serializers.complaint import ComplaintSerializer
from openprocurement.tender.core.procedure.serializers.document import ConfidentialDocumentSerializer


class CancellationSerializer(BaseSerializer):
    serializers = {
        "complaints": ListSerializer(ComplaintSerializer),
        "documents": ListSerializer(ConfidentialDocumentSerializer),
    }
