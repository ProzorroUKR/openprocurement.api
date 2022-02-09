from openprocurement.tender.core.procedure.serializers.base import BaseSerializer, ListSerializer
from openprocurement.tender.cfaua.procedure.serializers.contract import ContractSerializer


class AgreementSerializer(BaseSerializer):
    serializers = {
        "contracts": ListSerializer(ContractSerializer),
    }
