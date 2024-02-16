from uuid import uuid4

import standards
from schematics.exceptions import ValidationError
from schematics.types import MD5Type, StringType
from schematics.types.serializable import serializable

from openprocurement.api.procedure.models.base import Model
from openprocurement.api.procedure.types import IsoDateTimeType, ListType
from openprocurement.api.utils import get_now

RATIONALE_TYPES = tuple(standards.load("codelists/contract_change_rationale_type.json").keys())


class BaseChange(Model):
    rationale = StringType(required=True, min_length=1)
    rationale_en = StringType()
    rationale_ru = StringType()
    rationaleTypes = ListType(
        StringType(
            choices=RATIONALE_TYPES,
            required=True,
        ),
        min_size=1,
        required=True,
    )
    contractNumber = StringType()
    dateSigned = IsoDateTimeType()


class PostChange(BaseChange):
    @serializable
    def id(self):
        return uuid4().hex

    @serializable
    def status(self):
        return "pending"

    @serializable
    def date(self):
        return get_now().isoformat()

    def validate_dateSigned(self, data, value):
        validate_date_signed(data, value)


class PatchChange(BaseChange):
    status = StringType(choices=["pending", "active"])
    rationale = StringType(min_length=1)
    rationaleTypes = ListType(
        StringType(
            choices=RATIONALE_TYPES,
            required=True,
        ),
        min_size=1,
    )


class Change(BaseChange):
    id = MD5Type(required=True)
    status = StringType(choices=["pending", "active"])
    date = IsoDateTimeType()

    def validate_dateSigned(self, data, value):
        validate_date_signed(data, value)


def validate_date_signed(change, date_signed):
    if date_signed and date_signed > get_now():
        raise ValidationError("Contract signature date can't be in the future")
