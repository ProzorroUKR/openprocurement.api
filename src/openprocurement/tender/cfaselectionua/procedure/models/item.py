from openprocurement.api.models import Value
from openprocurement.tender.core.procedure.models.item import Item as BaseItem, Unit
from openprocurement.tender.core.procedure.models.base import ModelType


class ContractUnit(Unit):
    value = ModelType(Value)


class ContractItem(BaseItem):
    unit = ModelType(ContractUnit)
