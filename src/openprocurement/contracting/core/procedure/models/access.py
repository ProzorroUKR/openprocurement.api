from enum import StrEnum

from schematics.types import StringType

from openprocurement.api.procedure.models.base import Model


class ContractRole(StrEnum):
    BUYER = "buyer"
    SUPPLIER = "supplier"


class AccessRole(StrEnum):
    BUYER = ContractRole.BUYER.value
    SUPPLIER = ContractRole.SUPPLIER.value
    TENDER = "tender"  # deprecated
    BID = "bid"  # deprecated
    CONTRACT = "contract"  # deprecated


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
