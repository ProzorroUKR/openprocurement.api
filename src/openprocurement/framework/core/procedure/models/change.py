from uuid import uuid4

from schematics.exceptions import ValidationError
from schematics.types import MD5Type, StringType
from schematics.types.serializable import serializable

from openprocurement.api.constants import PERIOD_CHANGE_CAUSES
from openprocurement.api.procedure.models.base import Model
from openprocurement.api.procedure.models.period import PeriodEndRequired
from openprocurement.api.procedure.types import IsoDateTimeType, ListType, ModelType
from openprocurement.framework.core.procedure.models.document import (
    Document,
    PostDocument,
)


class Modifications(Model):
    qualificationPeriod = ModelType(PeriodEndRequired)


class PostChange(Model):
    @serializable
    def id(self):
        return uuid4().hex

    rationale = StringType(required=True, min_length=1)
    rationale_en = StringType()
    rationaleType = StringType(
        choices=list(PERIOD_CHANGE_CAUSES.keys()),
        required=True,
    )
    modifications = ModelType(Modifications, required=True)
    documents = ListType(ModelType(PostDocument, required=True), default=[])

    def validate_rationale(self, data, value):
        if data.get("rationaleType") != "other" and value != PERIOD_CHANGE_CAUSES.get(data["rationaleType"]):
            raise ValidationError("Value should be from dictionary `framework_period_change_causes`.")


class Change(Model):
    id = MD5Type()
    date = IsoDateTimeType()
    dateModified = IsoDateTimeType()
    rationale = StringType(required=True, min_length=1)
    rationale_en = StringType()
    rationaleType = StringType(
        choices=list(PERIOD_CHANGE_CAUSES.keys()),
        required=True,
    )
    modifications = ModelType(Modifications, required=True)
    previous = ModelType(Modifications, required=True)
    documents = ListType(ModelType(Document, required=True))
