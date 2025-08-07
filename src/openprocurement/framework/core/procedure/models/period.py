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


class PostPeriodChange(Model):
    @serializable
    def id(self):
        return uuid4().hex

    qualificationPeriod = ModelType(PeriodEndRequired, required=True)
    cause = StringType(required=True)
    causeDescription = StringType(required=True)
    documents = ListType(ModelType(PostDocument, required=True), default=[])

    def validate_cause(self, data, value):
        if value not in PERIOD_CHANGE_CAUSES.keys():
            raise ValidationError(f"Value must be one of {list(PERIOD_CHANGE_CAUSES.keys())}.")

    def validate_causeDescription(self, data, value):
        if data.get("cause") != "other" and value != PERIOD_CHANGE_CAUSES.get(data.get("cause")):
            raise ValidationError("Value should be from dictionary `framework_period_change_causes`.")


class PeriodChangeHistory(Model):
    id = MD5Type()
    prevPeriodEndDate = IsoDateTimeType()
    newPeriodEndDate = IsoDateTimeType()
    date = IsoDateTimeType()
    cause = StringType()
    causeDescription = StringType()
    documents = ListType(ModelType(Document, required=True))
