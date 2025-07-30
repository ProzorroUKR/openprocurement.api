from uuid import uuid4

from schematics.types import MD5Type, StringType
from schematics.types.serializable import serializable

from openprocurement.api.context import get_request_now
from openprocurement.api.procedure.models.base import Model
from openprocurement.api.procedure.types import IsoDateTimeType


class PostCancellation(Model):
    @serializable
    def id(self):
        return uuid4().hex

    @serializable
    def dateCreated(self):
        return get_request_now().isoformat()

    @serializable
    def status(self):
        return "pending"

    reason = StringType(required=True)
    reasonType = StringType(
        required=True,
        choices=[
            "requiresChanges",
        ],
    )


class PostChangeCancellation(PostCancellation):
    reasonType = StringType(
        required=True,
        choices=[
            "noDemand",
            "unFixable",
            "forceMajeure",
            "expensesCut",
        ],
    )


class Cancellation(Model):
    id = MD5Type(required=True)
    status = StringType(required=True, choices=["pending", "active"])
    reason = StringType(required=True)
    reasonType = StringType(
        required=True,
        choices=[
            "requiresChanges",
            "noDemand",
            "unFixable",
            "forceMajeure",
            "expensesCut",
        ],
    )
    dateCreated = IsoDateTimeType(required=True)
    author = StringType()
