from schematics.types import StringType
from schematics.types.compound import ModelType

from openprocurement.api.models import (
    Model,
    ListType,
    IsoDateTimeType,
    Guarantee,
    BankAccount,
)

from openprocurement.contracting.api.procedure.models.document import TransactionDocument


class OrganizationReference(Model):
    bankAccount = ModelType(BankAccount, required=True)
    name = StringType(required=True)


class PutTransaction(Model):
    date = IsoDateTimeType(required=True)
    value = ModelType(Guarantee, required=True)
    payer = ModelType(OrganizationReference, required=True)
    payee = ModelType(OrganizationReference, required=True)
    status = StringType(required=True)


class Transaction(PutTransaction):
    id = StringType(required=True)
    documents = ListType(ModelType(TransactionDocument))
