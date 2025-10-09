from typing import Any

from pydantic import BaseModel

from openprocurement.api.procedure.serializers.base import (
    BaseSerializer as ProcedureBaseSerializer,
)


class BaseSerializer(ProcedureBaseSerializer):
    def __init__(self, data: BaseModel | dict[str, Any], **kwargs):
        if isinstance(data, BaseModel):
            data = data.model_dump(mode="json", exclude_none=True, exclude_unset=True, warnings=False)
        super().__init__(data, **kwargs)
