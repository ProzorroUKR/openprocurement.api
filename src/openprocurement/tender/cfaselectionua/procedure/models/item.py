from openprocurement.api.procedure.models.unit import Unit
from openprocurement.api.procedure.types import ModelType
from openprocurement.tender.cfaselectionua.procedure.models.address import Address
from openprocurement.tender.core.procedure.models.item import (
    TechFeatureItem as BaseItem,
)


class ContractItem(BaseItem):
    unit = ModelType(Unit)
    deliveryAddress = ModelType(Address)

    def validate_unit(self, data, value):
        pass


class Item(ContractItem):
    pass
