from schematics.exceptions import ValidationError
from schematics.types import StringType

from openprocurement.api.constants import (
    VALIDATE_ADDRESS_FROM,
    COUNTRIES,
    UA_REGIONS,
    REQUIRED_FIELDS_BY_SUBMISSION_FROM,
)
from openprocurement.api.context import get_now
from openprocurement.api.models import BaseAddress
from openprocurement.api.utils import get_first_revision_date
from openprocurement.framework.core.procedure.context import get_object
from openprocurement.framework.core.procedure.utils import required_field_from_date


class CoreAddress(BaseAddress):
    def validate_countryName(self, data, value):
        if get_first_revision_date(get_object("framework"), default=get_now()) >= VALIDATE_ADDRESS_FROM:
            if value not in COUNTRIES:
                raise ValidationError("field address:countryName not exist in countries catalog")

    def validate_region(self, data, value):
        if get_first_revision_date(get_object("framework"), default=get_now()) >= VALIDATE_ADDRESS_FROM:
            if data["countryName"] == "Україна":
                if value and value not in UA_REGIONS:
                    raise ValidationError("field address:region not exist in ua_regions catalog")


class Address(CoreAddress):
    streetAddress = StringType(required=True)
    locality = StringType(required=True)
    region = StringType(required=True)
    postalCode = StringType(required=True)


class SubmissionAddress(CoreAddress):

    @required_field_from_date(REQUIRED_FIELDS_BY_SUBMISSION_FROM)
    def validate_region(self, data, value):
        super().validate_region(self, data, value)
        return value

    @required_field_from_date(REQUIRED_FIELDS_BY_SUBMISSION_FROM)
    def validate_postalCode(self, data, value):
        return value

    @required_field_from_date(REQUIRED_FIELDS_BY_SUBMISSION_FROM)
    def validate_locality(self, data, value):
        return value

    @required_field_from_date(REQUIRED_FIELDS_BY_SUBMISSION_FROM)
    def validate_streetAddress(self, data, value):
        return value
