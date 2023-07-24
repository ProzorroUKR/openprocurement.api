from openprocurement.tender.core.procedure.serializers.base import BaseSerializer, ListSerializer
from openprocurement.tender.core.procedure.serializers.document import ConfidentialDocumentSerializer


class ComplaintObjectionArgumentEvidenceSerializer(BaseSerializer):
    serializers = {
        "documents": ListSerializer(ConfidentialDocumentSerializer),
    }


class ComplaintObjectionArgumentSerializer(BaseSerializer):
    serializers = {
        "evidences": ListSerializer(ComplaintObjectionArgumentEvidenceSerializer),
    }
