from enum import StrEnum

from schematics.types import StringType

from openprocurement.api.procedure.models.base import Model


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
