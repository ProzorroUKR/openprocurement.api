from openprocurement.api.models import Value
from openprocurement.tender.core.procedure.models.item import Item as BaseItem
from openprocurement.tender.core.procedure.models.base import ModelType
from openprocurement.tender.core.procedure.models.unit import UnitDeprecated


class ContractUnit(UnitDeprecated):
    value = ModelType(Value)


class ContractItem(BaseItem):
    unit = ModelType(ContractUnit)

    def validate_unit(self, data, value):
        pass


class Item(ContractItem):
    pass
