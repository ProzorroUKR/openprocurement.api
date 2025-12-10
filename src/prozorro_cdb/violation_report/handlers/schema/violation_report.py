from pydantic import Field, field_validator
from pydantic_core import PydanticCustomError

from prozorro_cdb.api.handlers.schema.common import BaseRequestModel
from prozorro_cdb.violation_report.database.schema.violation_report import (
    ViolationReportReason,
    ViolationReportStatus,
)
from prozorro_cdb.violation_report.handlers.schema.constants import (
    TEXT_FIELD_MAX_LENGTH,
)
from prozorro_cdb.violation_report.handlers.schema.document import PostDocument


# post
class ReportDetailsPostRequestData(BaseRequestModel):
    reason: ViolationReportReason
    description: str = Field(description="Деталі порушення", max_length=TEXT_FIELD_MAX_LENGTH)
    documents: list[PostDocument] = Field(
        default_factory=list,
        description="Документи Замовника (скаржника)",
    )


class ViolationReportPostRequestData(BaseRequestModel):
    details: ReportDetailsPostRequestData
    status: ViolationReportStatus = ViolationReportStatus.draft

    @field_validator("status", mode="after")
    @classmethod
    def validate_status(cls, status: ViolationReportStatus) -> ViolationReportStatus:
        if status != ViolationReportStatus.draft:
            raise PydanticCustomError(
                "status_error",
                "{status} should be draft.",
                {"status": status},
            )
        return status


# patch
class ReportDetailsPatchRequestData(BaseRequestModel):
    reason: ViolationReportReason
    description: str = Field(description="Деталі порушення", max_length=TEXT_FIELD_MAX_LENGTH)


class ViolationReportPatchDetailsRequestData(BaseRequestModel):
    details: ReportDetailsPatchRequestData


class ViolationReportPublishRequestData(BaseRequestModel):
    status: ViolationReportStatus

    @field_validator("status", mode="after")
    @classmethod
    def validate_x(cls, status: ViolationReportStatus) -> ViolationReportStatus:
        if status != ViolationReportStatus.pending:
            raise PydanticCustomError(
                "status_error",
                "{status} should be pending.",
                {"status": status},
            )
        return status
