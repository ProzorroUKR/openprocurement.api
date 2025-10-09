from typing import Optional, Self

from pydantic import Field, field_validator, model_validator
from pydantic_core import PydanticCustomError

from openprocurement.api.models_async.common import BaseModel
from openprocurement.violation_report.database.schema.violation_report import (
    ViolationReportReason,
    ViolationReportStatus,
)
from openprocurement.violation_report.handlers.schema.document import RequestDocument


# post
class ReportDetailsRequestData(BaseModel):
    reason: ViolationReportReason
    description: str = Field(default="", description="Суть порушення", max_length=5_000)
    documents: list[RequestDocument] = Field(
        default_factory=list,
        description="Документи Замовника (скаржника)",
    )


class ViolationReportPostRequestData(BaseModel):
    details: ReportDetailsRequestData
    status: ViolationReportStatus = ViolationReportStatus.draft

    @field_validator("status", mode="after")
    @classmethod
    def validate_x(cls, status: ViolationReportStatus) -> ViolationReportStatus:
        if status not in (ViolationReportStatus.draft, ViolationReportStatus.pending):
            raise PydanticCustomError(
                "status_error",
                "{status} should be draft or pending.",
                {"status": status},
            )
        return status


# patch
class ReportDetailsPatchRequestData(BaseModel):
    description: str = Field(default="", description="Суть порушення", max_length=5_000)


class ViolationReportPatchRequestData(BaseModel):
    details: Optional[ReportDetailsPatchRequestData] = None
    status: Optional[ViolationReportStatus] = None

    @model_validator(mode="after")
    def check_passwords_match(self) -> Self:
        if self.details is None and self.status is None:
            raise ValueError("There is no changes.")
        return self

    @field_validator("status", mode="after")
    @classmethod
    def validate_x(cls, status: Optional[ViolationReportStatus]) -> Optional[ViolationReportStatus]:
        if status not in (ViolationReportStatus.draft, ViolationReportStatus.pending, None):
            raise PydanticCustomError(
                "status_error",
                "{status} should be draft or pending.",
                {"status": status},
            )
        return status
