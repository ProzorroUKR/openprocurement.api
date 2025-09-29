from schematics.types import StringType
from schematics.types.compound import ModelType

from openprocurement.api.procedure.models.bank import BankAccount
from openprocurement.api.procedure.models.base import Model
from openprocurement.api.procedure.models.value import BasicValue
from openprocurement.api.procedure.types import IsoDateTimeType, ListType
from openprocurement.contracting.core.procedure.models.document import (
    TransactionDocument,
)


class OrganizationReference(Model):
    bankAccount = ModelType(BankAccount, required=True)
    name = StringType(required=True)


class PutTransaction(Model):
    date = IsoDateTimeType(required=True)
    value = ModelType(BasicValue, required=True)
    payer = ModelType(OrganizationReference, required=True)
    payee = ModelType(OrganizationReference, required=True)
    status = StringType(required=True)


class Transaction(PutTransaction):
    id = StringType(required=True)
    documents = ListType(ModelType(TransactionDocument))
