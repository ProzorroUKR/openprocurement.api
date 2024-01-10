from openprocurement.tender.openua.procedure.models.item import Item
from openprocurement.api.procedure.types import ListType, ModelType
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
