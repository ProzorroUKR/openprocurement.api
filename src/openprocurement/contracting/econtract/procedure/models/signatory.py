from schematics.types import StringType

from openprocurement.api.context import get_request_now
from openprocurement.api.procedure.models.base import Model
from openprocurement.api.procedure.types import IsoDateTimeType


class PostSignatory(Model):
    pass


class Signatory(Model):
    role = StringType(choices=["buyer", "supplier"])
    date = IsoDateTimeType(default=get_request_now)
    # todo: think on how to identify who confirmed the signatory when supplier count will be more than 1
