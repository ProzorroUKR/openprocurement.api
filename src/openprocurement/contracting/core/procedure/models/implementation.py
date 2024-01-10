from schematics.types.compound import ModelType

from openprocurement.api.procedure.models.base import Model
from openprocurement.api.procedure.types import ListType
from openprocurement.contracting.core.procedure.models.transaction import Transaction


class Implementation(Model):
    transactions = ListType(ModelType(Transaction), default=list())
