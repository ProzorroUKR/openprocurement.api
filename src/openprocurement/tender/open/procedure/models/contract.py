from openprocurement.tender.open.procedure.models.item import Item
from openprocurement.tender.core.procedure.models.base import ModelType, ListType
from openprocurement.tender.core.procedure.models.contract import (
    PatchContractSupplier as BasePatchContractSupplier,
    PatchContract as BasePatchContract,
    Contract as BaseContract,
)


class Contract(BaseContract):
    items = ListType(ModelType(Item, required=True))


class PostContract(Contract):
    pass


class PatchContract(BasePatchContract):
    items = ListType(ModelType(Item, required=True))


class PatchContractSupplier(BasePatchContractSupplier):
    pass
