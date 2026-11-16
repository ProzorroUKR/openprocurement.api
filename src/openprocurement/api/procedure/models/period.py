from pydantic import model_validator

from openprocurement.api.procedure.errors import FieldError
from openprocurement.api.procedure.models.base import Model
from openprocurement.api.procedure.types import IsoDateTime


class Period(Model):
    startDate: IsoDateTime | None = None  # The state date for the period.
    endDate: IsoDateTime | None = None  # The end date for the period.

    @model_validator(mode="after")
    def validate_dates(self):
        if self.startDate and self.endDate and self.endDate < self.startDate:
            raise FieldError("startDate", "period should begin before its end")
        return self


class PeriodEndRequired(Period):
    endDate: IsoDateTime
