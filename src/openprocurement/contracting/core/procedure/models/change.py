import standards
from schematics.types import BaseType, MD5Type, StringType

from openprocurement.api.procedure.models.base import Model
from openprocurement.api.procedure.types import IsoDateTimeType, ListType

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


class Change(BaseChange):
    id = MD5Type(required=True)
    status = StringType(choices=["pending", "active"])
    date = IsoDateTimeType()
    contractNumber = StringType()
    dateSigned = IsoDateTimeType()
    modifications = BaseType()
    documents = BaseType()
    cancellations = BaseType()
    author = StringType()
