from typing import Any

from pydantic import BaseModel

from openprocurement.api.procedure.serializers.base import (
    BaseSerializer as ProcedureBaseSerializer,
)
from openprocurement.api.procedure.serializers.base import (
    ListSerializer as BaseListSerializer,
)
from prozorro_cdb.api.context import get_request_async


class BaseSerializer(ProcedureBaseSerializer):
    def __init__(self, data: BaseModel | dict[str, Any], **kwargs):
        if isinstance(data, BaseModel):
            data = data.model_dump(mode="json", exclude_none=True, warnings=False)
        super().__init__(data, **kwargs)

    def get_optional_fields(self) -> set[str]:
        return set(get_request_async().query.get("opt_fields", "").split(","))


class ListSerializer(BaseListSerializer):
    pass


class HideDraftListSerializer(ListSerializer):
    def __call__(self, data: list[dict[str, Any]], **kwargs) -> ListSerializer:
        # remove drafts from response
        objects = []
        for d in data:
            if d.get("status") != "draft":
                objects.append(d)
        return super().__call__(list(reversed(objects)), **kwargs)
