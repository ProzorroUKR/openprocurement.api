from openprocurement.api.models import IsoDateTimeType, ValidationError, Value, Period, ListType, Model
from openprocurement.tender.core.procedure.context import get_tender, get_now
from schematics.types import StringType, MD5Type, BooleanType, BaseType
from schematics.types.compound import PolyModelType
from schematics.types.serializable import serializable
from uuid import uuid4


class Contract(Model):
    id = MD5Type(required=True)
