from openprocurement.api.procedure.types import ListType, ModelType
from openprocurement.tender.competitivedialogue.procedure.models.item import Item
from openprocurement.tender.openeu.procedure.models.contract import (
    Contract as EUBaseContract,
)
from openprocurement.tender.openeu.procedure.models.contract import (
    PatchContract as EUBasePatchContract,
)
from openprocurement.tender.openeu.procedure.models.contract import (
    PatchContractSupplier as EUBasePatchContractSupplier,
)
from openprocurement.tender.openua.procedure.models.contract import (
    Contract as UABaseContract,
)
from openprocurement.tender.openua.procedure.models.contract import (
    PatchContract as UABasePatchContract,
)
from openprocurement.tender.openua.procedure.models.contract import (
    PatchContractSupplier as UABasePatchContractSupplier,
)


class UAContract(UABaseContract):
    items = ListType(ModelType(Item, required=True))


class UAPostContract(UAContract):
    pass


class UAPatchContract(UABasePatchContract):
    items = ListType(ModelType(Item, required=True))


class UAPatchContractSupplier(UABasePatchContractSupplier):
    pass


class EUContract(EUBaseContract):
    items = ListType(ModelType(Item, required=True))


class EUPostContract(EUContract):
    pass


class EUPatchContract(EUBasePatchContract):
    items = ListType(ModelType(Item, required=True))


class EUPatchContractSupplier(EUBasePatchContractSupplier):
    pass
