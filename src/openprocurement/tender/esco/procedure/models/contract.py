from openprocurement.tender.esco.procedure.models.value import ContractESCOValue
from openprocurement.tender.core.procedure.models.base import (
    ModelType, ListType,
)
from openprocurement.tender.core.procedure.models.contract import (
    PatchContractSupplier as BasePatchContractSupplier,
    PatchContract as BasePatchContract,
    Contract as BaseContract,
)
from openprocurement.tender.esco.procedure.models.item import Item


class Contract(BaseContract):
    value = ModelType(ContractESCOValue)
    items = ListType(ModelType(Item, required=True))


class PostContract(Contract):
    pass


class PatchContract(BasePatchContract):
    value = ModelType(ContractESCOValue)
    items = ListType(ModelType(Item, required=True))


class PatchContractSupplier(BasePatchContractSupplier):
    pass

