from typing import Generic, TypeVar

from prozorro_cdb.api.database.schema.common import BaseModel

DataT = TypeVar("DataT")


class DataModel(BaseModel, Generic[DataT]):
    data: DataT
