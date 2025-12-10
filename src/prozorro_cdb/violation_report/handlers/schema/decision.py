from typing import Literal

from pydantic import Field

from prozorro_cdb.api.handlers.schema.common import BaseRequestModel
from prozorro_cdb.api.handlers.schema.document import PostDocument
from prozorro_cdb.violation_report.database.schema.violation_report import (
    ViolationReportResolution,
)
from prozorro_cdb.violation_report.handlers.schema.constants import (
    TEXT_FIELD_MAX_LENGTH,
)


class DecisionPostRequestData(BaseRequestModel):
    resolution: ViolationReportResolution
    description: str = Field(
        description="Обґрунтування рішення",
        max_length=TEXT_FIELD_MAX_LENGTH,
    )
    documents: list[PostDocument] = Field(
        default_factory=list,
        description="Документи",
    )


class DecisionPatchRequestData(BaseRequestModel):
    resolution: ViolationReportResolution
    description: str = Field(
        description="Пояснення/контраргументи постачальника",
        max_length=TEXT_FIELD_MAX_LENGTH,
    )


class DecisionActivateRequestData(BaseRequestModel):
    status: Literal["active"] = Field(description="Статус (відправляється для публікації об'єкта)")
