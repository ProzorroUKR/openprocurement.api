from openprocurement.api.procedure.models.base import Model
from openprocurement.framework.cfaua.procedure.models.value import Value


class UnitPrice(Model):
    relatedItem: str | None = None
    value: Value | None = None
