from uuid import uuid4
from schematics.types import MD5Type, StringType, BaseType, BooleanType
from schematics.types.serializable import serializable

from openprocurement.api.procedure.models.base import Model
from openprocurement.api.procedure.types import ModelType, IsoDateTimeType
from openprocurement.api.utils import get_now
from openprocurement.framework.core.procedure.models.organization import Organization


class Question(Model):
    id = MD5Type(required=True, default=lambda: uuid4().hex)
    author = ModelType(
        Organization, required=True
    )  # who is asking question (contactPoint - person, identification - organization that person represents)
    title = StringType(required=True)  # title of the question
    description = StringType()  # description of the question
    date = IsoDateTimeType()  # autogenerated date of posting
    answer = StringType()  # only framework owner can post answer
    dateAnswered = IsoDateTimeType()  # date of answer


class PostQuestion(Model):
    @serializable
    def id(self):
        return uuid4().hex

    @serializable
    def date(self):
        return get_now().isoformat()

    author = ModelType(
        Organization, required=True
    )
    title = StringType(required=True)
    description = StringType()


class PatchQuestion(Model):
    answer = StringType(required=True)
