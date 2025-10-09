from pydantic import Field

from openprocurement.api.models_async.common import BaseModel


class DefendantStatementRequestData(BaseModel):
    description: str = Field(
        default="",
        description="Пояснення/контраргументи постачальника",
        max_length=5_000,
    )
