from typing import Any, Literal
from uuid import uuid4

from pydantic import computed_field, field_serializer

from openprocurement.api.context import get_request_now
from openprocurement.api.procedure.errors import ValidationError
from openprocurement.api.procedure.models.base import Model, model_field_validator
from openprocurement.api.procedure.types import (
    MD5,
    IsoDateTime,
)
from openprocurement.tender.core.procedure.models.document import Document
from openprocurement.tender.core.procedure.utils import tender_created_after_2020_rules


class PostCancellation(Model):
    @computed_field
    def id(self) -> Any:
        return uuid4().hex

    @computed_field
    def date(self) -> Any:
        return get_request_now().isoformat()

    @computed_field
    def cancellationOf(self) -> Any:
        return "lot" if self.relatedLot else "tender"

    status: Literal["draft", "pending", "active"] | None = None

    @field_serializer("status")
    def serialize_status(self, value: Any) -> Any:
        if tender_created_after_2020_rules():
            return "draft"
        elif not value:
            return "pending"
        return value

    reasonType: str | None = None
    reason: str
    reason_en: str | None = None
    reason_ru: str | None = None
    documents: list[Document] | None = None
    relatedLot: MD5 | None = None

    @model_field_validator("relatedLot")
    def validate_related_lot(self, related_lot):
        if not related_lot and self.cancellationOf == "lot":
            raise ValidationError("This field is required.")


class PatchCancellation(Model):
    status: Literal["draft", "pending", "active", "unsuccessful"] | None = None
    reasonType: str | None = None


class Cancellation(Model):
    id: MD5
    status: Literal["draft", "pending", "active", "unsuccessful"]
    date: IsoDateTime
    reasonType: str | None = None
    reason: str
    reason_en: str | None = None
    reason_ru: str | None = None
    cancellationOf: Literal["lot", "tender"]
    relatedLot: MD5 | None = None
    complaints: Any = None
    complaintPeriod: Any = None
    documents: Any = None
