from pydantic import Field

from openprocurement.api.models_async.common import BaseModel
from openprocurement.violation_report.handlers.schema.document import RequestDocument


class DefendantStatementRequestData(BaseModel):
    description: str = Field(
        default="",
        description="Пояснення/контраргументи постачальника",
        max_length=5_000,
    )
    documents: list[RequestDocument] = Field(
        min_length=2,
        description="Документи постачальника",
    )
