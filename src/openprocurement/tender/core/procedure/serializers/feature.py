from openprocurement.tender.core.procedure.serializers.base import BaseSerializer, ListSerializer


def enum_serializer(_, element):
    if isinstance(element, dict) and isinstance(element.get("value"), str):
        element["value"] = float(element["value"])
    return element


class FeatureSerializer(BaseSerializer):
    serializers = {
        "enum": ListSerializer(enum_serializer),
    }
