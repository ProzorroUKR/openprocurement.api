from typing import Generic, TypeVar

from pydantic import BaseModel, ConfigDict

DataT = TypeVar("DataT")


class BaseRequestModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class DataModel(BaseRequestModel, Generic[DataT]):
    data: DataT
