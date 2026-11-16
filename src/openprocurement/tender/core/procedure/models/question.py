from typing import Any, Literal
from uuid import uuid4

from pydantic import Field, computed_field

from openprocurement.api.context import get_request_now
from openprocurement.api.procedure.errors import ValidationError
from openprocurement.api.procedure.models.base import Model, model_field_validator
from openprocurement.api.procedure.types import (
    MD5,
    IsoDateTime,
)
from openprocurement.tender.core.procedure.models.organization import Organization


class PostQuestion(Model):
    @computed_field
    def id(self) -> Any:
        return uuid4().hex

    @computed_field
    def date(self) -> Any:
        return get_request_now().isoformat()

    author: Organization
    title: str
    description: str | None = None
    questionOf: Literal["tender", "item", "lot"] = "tender"
    relatedItem: str | None = Field(None, min_length=1)

    @model_field_validator("relatedItem")
    def validate_related_item(self, related_item):
        if not related_item and self.questionOf in ("item", "lot"):
            raise ValidationError("This field is required.")


class PatchQuestion(Model):
    answer: str


class Question(Model):
    id: MD5
    author: Organization
    title: str
    description: str | None = None
    date: IsoDateTime | None = None
    answer: str | None = None
    questionOf: Literal["tender", "item", "lot"] = "tender"
    relatedItem: str | None = Field(None, min_length=1)
    dateAnswered: IsoDateTime | None = None


def validate_questions_related_items(tender, questions):
    if questions:
        item_ids = {i.id for i in getattr(tender, "items", None) or []}  # not fields of all the tenders
        lot_ids = {i.id for i in getattr(tender, "lots", None) or []}

        for q in questions:
            related_item = q.relatedItem
            question_of = q.questionOf
            if not related_item and question_of in ("item", "lot"):
                raise ValidationError("This field is required.")

            if question_of == "item":
                if related_item not in item_ids:
                    raise ValidationError([{"relatedItem": ["relatedItem should be one of items"]}])

            elif question_of == "lot" and related_item not in lot_ids:
                raise ValidationError([{"relatedItem": ["relatedItem should be one of lots"]}])
