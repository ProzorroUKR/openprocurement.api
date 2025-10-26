from __future__ import annotations

import inspect
from decimal import Decimal
from typing import Any, Callable, Generic, TypeVar, Union

from openprocurement.api.procedure.utils import to_decimal

T = TypeVar("T")


def evaluate_serializer(serializer: Callable, value: Any, **kwargs) -> Any:
    if len(inspect.signature(serializer).parameters) > 1:
        instance = serializer(value, **kwargs)
    else:
        instance = serializer(value)
    if issubclass(type(instance), AbstractSerializer):
        return instance.data
    return instance


class AbstractSerializer(Generic[T]):
    _data: Any
    _kwargs: dict[str, Any]

    @property
    def raw(self) -> Any:
        return self._data

    @property
    def data(self) -> T:
        return self._data

    @property
    def kwargs(self) -> dict[str, Any]:
        return self._kwargs


class BaseSerializer(AbstractSerializer[dict[str, Any]]):
    serializers: dict[str, Callable] = {}
    private_fields: list[str] | None = None
    whitelist: list[str] | None = None

    def __init__(self, data: dict[str, Any], **kwargs):
        self._data = data
        self._kwargs = kwargs.copy()

    @property
    def data(self) -> dict[str, Any]:
        return self.serialize(self.raw, **self.kwargs)

    def serialize(self, data: dict[str, Any], **kwargs) -> dict[str, Any]:
        # pre-serialize
        items = list(data.items())
        if self.private_fields:
            items = [(k, v) for k, v in items if k not in self.private_fields]
        if self.whitelist:
            items = [(k, v) for k, v in items if k in self.whitelist]

        # serialize
        serialized_data = {}
        for key, value in items:
            if value is None:  # model.model_dump(exclude_none=True) doesn't work for sub models
                continue

            serialized_value = self.serialize_value(key, value, **kwargs)

            # post-serialize
            if serialized_value is None:  # we don't show null in our outputs
                continue
            elif isinstance(serialized_value, list) and len(serialized_value) == 0:  # and empty lists
                continue

            # store serialized value
            serialized_data[key] = serialized_value

        return serialized_data

    def serialize_value(self, key: str, value: Any, **kwargs) -> Any:
        if serializer := self.serializers.get(key):
            return evaluate_serializer(serializer, value, **kwargs)
        return value


class ListSerializer(AbstractSerializer[list[Any]]):
    def __init__(self, serializer: Callable):
        self.serializer = serializer

    def __call__(self, data: list[Any], **kwargs) -> ListSerializer:
        self._data = data
        self._kwargs = kwargs.copy()
        return self

    @property
    def data(self) -> list[Any]:
        return self.serialize(self.raw, **self.kwargs)

    def serialize(self, data, **kwargs) -> list[Any]:
        serialized_data = []
        for item in data or []:
            serialized_value = self.serialize_value(item, **kwargs)
            serialized_data.append(serialized_value)
        return serialized_data

    def serialize_value(self, value: Any, **kwargs) -> Any:
        return evaluate_serializer(self.serializer, value, **kwargs)


class BaseUIDSerializer(BaseSerializer):
    un_underscore_fields = [
        "id",
        "rev",
        "attachments",
    ]

    def serialize(self, data: dict[str, Any], **kwargs) -> dict[str, Any]:
        data = data.copy()
        for field in self.un_underscore_fields:
            data[field] = data.pop(f"_{field}", None)
        return super().serialize(data, **kwargs)


def decimal_serializer(value: Union[int, float, str]) -> Decimal:
    return to_decimal(value)
