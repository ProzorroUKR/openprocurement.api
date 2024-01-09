from openprocurement.api.utils import to_decimal


def evaluate_serializer(serializer, value, obj=None):
    if type(serializer).__name__ == "function":
        value = serializer(obj, value)
    else:
        value = serializer(value).data
    return value


class ListSerializer:
    def __init__(self, serializer):
        self.serializer = serializer

    def __call__(self, data):
        self._data = data
        return self

    @property
    def data(self) -> list:
        if self._data:
            return [evaluate_serializer(self.serializer, e, self) for e in self._data]


class BaseSerializer:
    _data: dict
    serializers = {}
    private_fields = None
    whitelist = None
    # defaults = None

    def __init__(self, data: dict):
        self._data = data

    def get_raw(self, k):
        return self._data.get(k)

    @property
    def data(self) -> dict:
        items = ((k, v) for k, v in self._data.items())
        if self.private_fields:
            items = ((k, v)
                     for k, v in items
                     if k not in self.private_fields)
        if self.whitelist:
            items = ((k, v)
                     for k, v in items
                     if k in self.whitelist)

        data = {}
        for k, v in items:
            s = self.serialize_value(k, v)
            if s is None:  # we don't show null in our outputs
                continue
            elif isinstance(s, list) and len(s) == 0:  # and empty lists
                continue
            data[k] = s
        #
        # if self.defaults:
        #     for k, v in self.defaults.items():
        #         if k not in data:
        #             data[k] = v
        return data

    def serialize_value(self, key, value):
        serializer = self.serializers.get(key)
        if serializer:
            value = evaluate_serializer(serializer, value, self)
        return value


class BaseUIDSerializer(BaseSerializer):
    @property
    def data(self) -> dict:
        data = super().data
        data["id"] = data.pop("_id")
        return data


def decimal_serializer(_, value):
    return to_decimal(value)
