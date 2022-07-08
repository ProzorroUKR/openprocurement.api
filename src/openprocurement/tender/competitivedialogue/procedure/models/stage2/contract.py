from openprocurement.tender.core.procedure.models.base import ModelType, ListType
from openprocurement.tender.openeu.procedure.models.contract import (
    PatchContractSupplier as EUBasePatchContractSupplier,
    PatchContract as EUBasePatchContract,
    Contract as EUBaseContract,
)
from openprocurement.tender.openua.procedure.models.contract import (
    PatchContractSupplier as UABasePatchContractSupplier,
    PatchContract as UABasePatchContract,
    Contract as UABaseContract,
)
from openprocurement.tender.competitivedialogue.procedure.models.item import Item


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
