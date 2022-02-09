from openprocurement.tender.core.procedure.serializers.base import BaseSerializer, ListSerializer
from openprocurement.tender.cfaua.procedure.serializers.parameter import ParameterSerializer


class ContractSerializer(BaseSerializer):
    serializers = {
        "parameters": ListSerializer(ParameterSerializer),
    }

