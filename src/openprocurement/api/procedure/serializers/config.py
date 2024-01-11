from openprocurement.api.procedure.serializers.base import BaseSerializer


class BaseConfigSerializer(BaseSerializer):
    def __init__(self, data: dict):
        super().__init__(data)
        for field_name in self.serializers.keys():
            # If there is serializer for field
            # force it to be called
            # even if value is not present
            if field_name not in self._data:
                self._data[field_name] = None

    serializers = {}
