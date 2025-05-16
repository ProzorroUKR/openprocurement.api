from enum import StrEnum

from schematics.types import BooleanType, StringType
from schematics.types.serializable import serializable

from openprocurement.api.procedure.models.base import Model
from openprocurement.api.procedure.models.identifier import Identifier
from openprocurement.api.procedure.types import ModelType


class PostAccess(Model):
    identifier = ModelType(Identifier, required=True)

    @serializable
    def active(self):
        return False


class PatchAccess(Model):
    identifier = ModelType(Identifier, required=True)
    active = BooleanType(choices=[True], required=True)


class AccessRole(StrEnum):
    BUYER = "buyer"
    SUPPLIER = "supplier"
    # deprecated
    TENDER = "tender"
    BID = "bid"
    CONTRACT = "contract"


ACCESS_ROLE_CHOICES = [
    AccessRole.BUYER.value,
    AccessRole.SUPPLIER.value,
    AccessRole.TENDER.value,
    AccessRole.BID.value,
    AccessRole.CONTRACT.value,
]


class AccessDetails(Model):
    owner = StringType()
    token = StringType()
    role = StringType(choices=ACCESS_ROLE_CHOICES)
