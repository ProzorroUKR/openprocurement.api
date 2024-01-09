from openprocurement.api.procedure.serializers.base import ListSerializer, BaseSerializer
from openprocurement.tender.core.procedure.serializers.document import ConfidentialDocumentSerializer
from openprocurement.tender.core.procedure.serializers.complaint import ComplaintSerializer


class AwardSerializer(BaseSerializer):
    serializers = {
        "documents": ListSerializer(ConfidentialDocumentSerializer),
        "complaints": ListSerializer(ComplaintSerializer),
    }
