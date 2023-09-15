from schematics.types import StringType, EmailType
from schematics.types.compound import ModelType
from schematics.types.serializable import serializable

from openprocurement.api.models import (
    Model,
    ListType,
    IsoDateTimeType,
    Identifier,
    validate_telephone,
)

from openprocurement.contracting.core.procedure.models.contract_base import (
    Address,
    ContactPoint,
    AmountPaid,
    BasePostContract,
    BasePatchContract,
    BaseContract,
)
from openprocurement.tender.core.procedure.models.contract import validate_item_unit_values


class SignerInfo(Model):
    name = StringType(required=True)
    email = EmailType(required=True)
    telephone = StringType(required=True)
    iban = StringType(min_length=15, max_length=33, required=True)
    signerDocument = StringType(required=True)
    organizationStatus = StringType(required=True)

    def validate_telephone(self, data, value):
        validate_telephone(value)


class Buyer(Model):
    """An organization."""
    name = StringType(required=True)
    name_en = StringType()
    name_ru = StringType()
    identifier = ModelType(Identifier, required=True)
    additionalIdentifiers = ListType(ModelType(Identifier))
    additionalContactPoints = ListType(ModelType(ContactPoint, required=True), required=False)
    address = ModelType(Address, required=True)
    signerInfo = ModelType(SignerInfo)


class PostContract(BasePostContract):
    """
    Model only for auto-creating contract
    """

    @serializable
    def status(self):
        return "pending"

    amountPaid = ModelType(AmountPaid)
    contractTemplateUri = StringType()
    buyer = ModelType(
        Buyer, required=True
    )
    bid_owner = StringType(required=True)
    bid_token = StringType(required=True)


class PatchContract(BasePatchContract):
    status = StringType(choices=["pending", "pending.winner-signing",  "terminated", "active", "cancelled"])

    def validate_items(self, data, items):
        validate_item_unit_values(data, items)


class PatchContractPending(PatchContract):
    dateSigned = IsoDateTimeType()
    contractNumber = StringType()

    def validate_items(self, data, items):
        validate_item_unit_values(data, items)


class AdministratorPatchContract(Model):
    contractNumber = StringType()
    status = StringType(choices=["pending", "pending.winner-signing", "terminated", "active", "cancelled"])
    suppliers = ListType(ModelType(Buyer, required=True), min_size=1, max_size=1)
    buyer = ModelType(Buyer)
    mode = StringType(choices=["test"])


class Contract(BaseContract):
    status = StringType(choices=["pending", "pending.winner-signing", "terminated", "active", "cancelled"])
    buyer = ModelType(
        Buyer, required=True
    )
    suppliers = ListType(ModelType(Buyer, required=True), min_size=1, max_size=1)

    contractTemplateUri = StringType()

    bid_owner = StringType(required=True)
    bid_token = StringType(required=True)
