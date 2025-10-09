from pydantic import Field

from openprocurement.api.models_async.common import BaseModel
from openprocurement.violation_report.database.schema.violation_report import (
    ViolationReportDecisionStatus,
)
from openprocurement.violation_report.handlers.schema.document import RequestDocument


class DecisionRequestData(BaseModel):
    status: ViolationReportDecisionStatus
    description: str = Field(
        default="",
        description="Обґрунтування рішення",
        max_length=5_000,
    )
    documents: list[RequestDocument] = Field(
        min_length=1,
        description="Документи рішення",
    )
