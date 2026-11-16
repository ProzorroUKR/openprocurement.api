from typing import Any, Literal
from uuid import uuid4

from pydantic import Field, field_serializer

from openprocurement.api.constants import ProcurementMethodType
from openprocurement.api.procedure.context import get_tender
from openprocurement.api.procedure.errors import ValidationError
from openprocurement.api.procedure.models.base import model_field_validator
from openprocurement.api.procedure.models.period import Period
from openprocurement.api.procedure.types import (
    MD5,
    IsoDateTime,
)
from openprocurement.tender.core.procedure.models.document import Document
from openprocurement.tender.core.procedure.models.milestone import (
    QualificationMilestoneListMixin,
)
from openprocurement.tender.core.procedure.models.req_response import (
    ObjResponseMixin,
)


class PatchQualification(ObjResponseMixin):
    title: str | None = None
    title_en: str | None = None
    title_ru: str | None = None
    description: str | None = None
    description_en: str | None = None
    description_ru: str | None = None
    status: Literal["pending", "active", "unsuccessful", "cancelled"] | None = None
    qualified: bool | None = None
    eligible: bool | None = None


class Qualification(PatchQualification, QualificationMilestoneListMixin):
    id: MD5 = Field(default_factory=lambda: uuid4().hex)
    bidID: str
    lotID: MD5 | None = None
    status: Literal["pending", "active", "unsuccessful", "cancelled"] = "pending"
    date: IsoDateTime | None = None
    documents: list[Document] | None = None
    qualified: bool | None = None
    eligible: bool | None = None
    complaints: Any = None
    complaintPeriod: Period | None = None

    @staticmethod
    def should_be_qualified():
        # TODO: find a way to determine, not based on procurementMethodType
        return get_tender()["procurementMethodType"] not in (
            ProcurementMethodType.BELOW_THRESHOLD,
            ProcurementMethodType.REQUEST_FOR_PROPOSAL,
        )

    @staticmethod
    def should_be_eligible():
        # TODO: find a way to determine, not based on procurementMethodType
        return get_tender()["procurementMethodType"] not in (
            ProcurementMethodType.BELOW_THRESHOLD,
            ProcurementMethodType.REQUEST_FOR_PROPOSAL,
        )

    @field_serializer("qualified")
    def serialize_qualified(self, value: Any) -> Any:
        if value is None and self.should_be_qualified():
            return False
        return value

    @field_serializer("eligible")
    def serialize_eligible(self, value: Any) -> Any:
        if value is None and self.should_be_eligible():
            return False
        return value

    @model_field_validator("qualified")
    def validate_qualified(self, qualified):
        if not self.should_be_qualified():
            return
        status = self.status
        if status == "active" and qualified is not True:
            raise ValidationError("This field must be true.")

    @model_field_validator("eligible")
    def validate_eligible(self, eligible):
        if not self.should_be_eligible():
            return
        status = self.status
        if status == "active" and eligible is not True:
            raise ValidationError("This field must be true.")
