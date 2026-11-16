from pydantic import BaseModel, ConfigDict


class BaseRequestModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class DataModel[DataT](BaseRequestModel):
    data: DataT
