from uuid import uuid4

from schematics.exceptions import ValidationError
from schematics.types.serializable import serializable
from schematics.types import StringType, MD5Type

from openprocurement.api.procedure.models.base import Model
from openprocurement.api.procedure.types import ModelType, IsoDateTimeType
from openprocurement.api.context import get_now
from openprocurement.api.procedure.context import get_tender
from openprocurement.tender.core.procedure.models.organization import Organization


class PostQuestion(Model):
    @serializable
    def id(self):
        return uuid4().hex

    @serializable
    def date(self):
        return get_now().isoformat()

    author = ModelType(Organization, required=True)
    title = StringType(required=True)
    description = StringType()
    questionOf = StringType(required=True, choices=["tender", "item", "lot"], default="tender")
    relatedItem = StringType(min_length=1)

    def validate_relatedItem(self, data, related_item):
        if not related_item and data.get("questionOf") in ["item", "lot"]:
            raise ValidationError("This field is required.")
        if related_item:
            tender = get_tender()
            if data.get("questionOf") == "lot" and related_item not in [i["id"] for i in tender.get("lots", []) if i]:
                raise ValidationError("relatedItem should be one of lots")
            if data.get("questionOf") == "item" and related_item not in [i["id"] for i in tender.get("items", []) if i]:
                raise ValidationError("relatedItem should be one of items")


class PatchQuestion(Model):
    answer = StringType(required=True)


class Question(Model):
    id = MD5Type(required=True)
    author = ModelType(
        Organization, required=True
    )  # who is asking question (contactPoint - person, identification - organization that person represents)
    title = StringType(required=True)  # title of the question
    description = StringType()  # description of the question
    date = IsoDateTimeType()  # autogenerated date of posting
    answer = StringType()  # only tender owner can post answer
    questionOf = StringType(required=True, choices=["tender", "item", "lot"], default="tender")
    relatedItem = StringType(min_length=1)
    dateAnswered = IsoDateTimeType()


def validate_questions_related_items(data, questions):
    if questions:
        item_ids = {i.id for i in data.get("items") or []}
        lot_ids = {i.id for i in data.get("lots") or []}

        for q in questions:
            related_item = q.relatedItem
            question_of = q.questionOf
            if not related_item and question_of in ("item", "lot"):
                raise ValidationError("This field is required.")

            if question_of == "item":
                if related_item not in item_ids:
                    raise ValidationError([{'relatedItem': ['relatedItem should be one of items']}])

            elif question_of == "lot" and related_item not in lot_ids:
                raise ValidationError([{'relatedItem': ['relatedItem should be one of lots']}])
