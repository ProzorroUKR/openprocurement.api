

class ListSerializer:
    def __init__(self, cls):
        self.cls = cls

    def __call__(self, data):
        self._data = data
        return self

    @property
    def data(self) -> list:
        return [self.cls(e).data for e in self._data]


class BaseSerializer:
    _data: dict
    serializers = {}
    private_fields = None
    whitelist = None

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

        data = {
            k: self.serialize_value(k, v)
            for k, v in items
        }
        return data

    def serialize_value(self, key, value):
        serializer = self.serializers.get(key)
        if serializer:
            if type(serializer).__name__ == "function":
                value = serializer(self, value)
            else:
                value = serializer(value).data
        return value
