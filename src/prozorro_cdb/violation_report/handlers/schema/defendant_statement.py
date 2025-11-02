from typing import Literal

from pydantic import Field

from prozorro_cdb.api.handlers.schema.common import BaseRequestModel
from prozorro_cdb.violation_report.handlers.schema.constants import (
    TEXT_FIELD_MAX_LENGTH,
)
from prozorro_cdb.violation_report.handlers.schema.document import PostDocument


class DefendantStatementPostRequestData(BaseRequestModel):
    description: str = Field(
        description="Пояснення/контраргументи постачальника",
        max_length=TEXT_FIELD_MAX_LENGTH,
    )
    documents: list[PostDocument] = Field(
        default_factory=list,
        description="Документи відповідача (постачальника)",
    )


class DefendantStatementPatchRequestData(BaseRequestModel):
    description: str = Field(
        description="Пояснення/контраргументи постачальника",
        max_length=TEXT_FIELD_MAX_LENGTH,
    )


class DefendantStatementActivateRequestData(BaseRequestModel):
    status: Literal["active"] = Field(description="Статус (відправляється для публікації об'єкта)")
