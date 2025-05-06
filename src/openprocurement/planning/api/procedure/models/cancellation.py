from uuid import uuid4

from schematics.types import MD5Type, StringType
from schematics.types.serializable import serializable

from openprocurement.api.context import get_request_now
from openprocurement.api.procedure.models.base import Model
from openprocurement.api.procedure.types import IsoDateTimeType


class BaseCancellation(Model):
    reason = StringType(required=True, min_length=1)
    reason_en = StringType()
    status = StringType(choices=["pending", "active"], default="pending")


class PostCancellation(BaseCancellation):
    @serializable
    def id(self):
        return uuid4().hex

    @serializable
    def date(self):
        return get_request_now().isoformat()


class PatchCancellation(BaseCancellation):
    pass


class Cancellation(BaseCancellation):
    id = MD5Type(required=True, default=lambda: uuid4().hex)
    date = IsoDateTimeType(default=get_request_now)
