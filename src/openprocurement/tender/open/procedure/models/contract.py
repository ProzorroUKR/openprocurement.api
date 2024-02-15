from openprocurement.api.procedure.types import ListType, ModelType
from openprocurement.tender.core.procedure.models.contract import (
    Contract as BaseContract,
)
from openprocurement.tender.core.procedure.models.contract import (
    PatchContract as BasePatchContract,
)
from openprocurement.tender.core.procedure.models.contract import (
    PatchContractSupplier as BasePatchContractSupplier,
)
from openprocurement.tender.open.procedure.models.item import Item


class Contract(BaseContract):
    items = ListType(ModelType(Item, required=True))


class PostContract(Contract):
    pass


class PatchContract(BasePatchContract):
    items = ListType(ModelType(Item, required=True))


class PatchContractSupplier(BasePatchContractSupplier):
    pass
