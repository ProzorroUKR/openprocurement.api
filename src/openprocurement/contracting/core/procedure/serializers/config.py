from openprocurement.api.procedure.serializers.config import BaseConfigSerializer


def restricted_serializer(obj, value):
    if value is None:
        return False

    return value


class ContractConfigSerializer(BaseConfigSerializer):
    serializers = {
        "restricted": restricted_serializer,
    }
