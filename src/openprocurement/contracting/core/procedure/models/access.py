from enum import StrEnum

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


class AccessDetails(Model):
    owner: str | None = None
    token: str | None = None
    role: AccessRole | None = None
