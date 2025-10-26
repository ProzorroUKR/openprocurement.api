from pydantic import BaseModel, Field


class DefendantStatementRequestData(BaseModel):
    description: str = Field(
        default="",
        description="Пояснення/контраргументи постачальника",
        max_length=5_000,
    )
