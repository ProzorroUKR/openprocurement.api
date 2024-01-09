from schematics.exceptions import ValidationError

from openprocurement.api.procedure.models.base import Model
from openprocurement.api.procedure.types import IsoDateTimeType


class Period(Model):
    startDate = IsoDateTimeType()  # The state date for the period.
    endDate = IsoDateTimeType()  # The end date for the period.

    def validate_startDate(self, data, value):
        if value and data.get("endDate") and data.get("endDate") < value:
            raise ValidationError("period should begin before its end")


class PeriodEndRequired(Period):
    endDate = IsoDateTimeType(required=True)
