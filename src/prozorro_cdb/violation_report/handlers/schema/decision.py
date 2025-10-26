from pydantic import BaseModel, Field

from prozorro_cdb.violation_report.database.schema.violation_report import (
    ViolationReportDecisionStatus,
)


class DecisionRequestData(BaseModel):
    status: ViolationReportDecisionStatus
    description: str = Field(
        default="",
        description="Обґрунтування рішення",
        max_length=5_000,
    )
