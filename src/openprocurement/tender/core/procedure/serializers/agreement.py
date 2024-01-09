from openprocurement.api.procedure.serializers.base import ListSerializer, BaseSerializer
from openprocurement.tender.core.procedure.serializers.document import ConfidentialDocumentSerializer


class AgreementSerializer(BaseSerializer):
    serializers = {
        "documents": ListSerializer(ConfidentialDocumentSerializer),
    }
