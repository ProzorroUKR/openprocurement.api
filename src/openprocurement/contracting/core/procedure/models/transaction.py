from openprocurement.api.procedure.models.bank import BankAccount
from openprocurement.api.procedure.models.base import Model
from openprocurement.api.procedure.models.value import BasicValue
from openprocurement.api.procedure.types import (
    IsoDateTime,
)
from openprocurement.contracting.core.procedure.models.document import (
    TransactionDocument,
)


class OrganizationReference(Model):
    bankAccount: BankAccount
    name: str


class PutTransaction(Model):
    date: IsoDateTime
    value: BasicValue
    payer: OrganizationReference
    payee: OrganizationReference
    status: str


class Transaction(PutTransaction):
    id: str
    documents: list[TransactionDocument] | None = None
