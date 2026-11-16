from openprocurement.api.procedure.models.base import Model
from openprocurement.contracting.core.procedure.models.transaction import Transaction


class Implementation(Model):
    transactions: list[Transaction] = []
