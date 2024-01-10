from openprocurement.api.procedure.serializers.base import ListSerializer, BaseSerializer
from openprocurement.tender.cfaua.procedure.serializers.contract import ContractSerializer
from openprocurement.tender.core.procedure.serializers.document import ConfidentialDocumentSerializer


class AgreementSerializer(BaseSerializer):
    serializers = {
        "documents": ListSerializer(ConfidentialDocumentSerializer),
        "contracts": ListSerializer(ContractSerializer),
    }
