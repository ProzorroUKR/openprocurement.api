from openprocurement.api.procedure.serializers.base import ListSerializer, BaseSerializer
from openprocurement.tender.cfaua.procedure.serializers.parameter import ParameterSerializer


class ContractSerializer(BaseSerializer):
    serializers = {
        "parameters": ListSerializer(ParameterSerializer),
    }

