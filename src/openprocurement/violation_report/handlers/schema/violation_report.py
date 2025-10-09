from pydantic import Field

from openprocurement.api.models_async.common import BaseModel
from openprocurement.violation_report.database.schema.violation_report import (
    ViolationReportReason,
)
from openprocurement.violation_report.handlers.schema.document import RequestDocument


class ViolationReportDraftRequestData(BaseModel):
    reason: ViolationReportReason
    description: str = Field(default="", description="Суть порушення", max_length=5_000)
    documents: list[RequestDocument] = Field(
        min_length=2,
        description="Документи Замовника (скаржника)",
    )
