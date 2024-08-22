from openprocurement.api.procedure.serializers.base import BaseSerializer


class UnitPreQualificationSerializer(BaseSerializer):
    private_fields = {"value"}


class ItemPreQualificationSerializer(BaseSerializer):
    serializers = {
        "unit": UnitPreQualificationSerializer,
    }
