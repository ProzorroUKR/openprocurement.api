from schematics.types import StringType, EmailType
from schematics.types.compound import ModelType
from schematics.types.serializable import serializable

from openprocurement.api.models import (
    Model,
    BaseType,
    ListType,
    IsoDateTimeType,
    Identifier,
    validate_telephone,
)
from openprocurement.api.validation import validate_items_uniq

from openprocurement.contracting.core.procedure.models.contract_base import Item as BaseItem
from openprocurement.contracting.core.procedure.models.contract_base import (
    Address,
    ContactPoint,
    AmountPaid,
    BasePostContract,
    BasePatchContract,
    BaseContract,
)
from openprocurement.contracting.econtract.procedure.models.value import ContractValue
from openprocurement.tender.core.procedure.models.contract import validate_item_unit_values
from openprocurement.tender.core.procedure.models.unit import Unit


class SignerInfo(Model):
    name = StringType(min_length=1, required=True)
    email = EmailType(min_length=1, required=True)
    telephone = StringType(min_length=1, required=True)
    iban = StringType(min_length=15, max_length=33, required=True)
    position = StringType(min_length=1, required=True)
    authorizedBy = StringType(min_length=1, required=True)

    def validate_telephone(self, data, value):
        validate_telephone(value)


class Attribute(Model):
    name = StringType(required=True)
    unit = ModelType(Unit)
    values = ListType(BaseType(required=True))


class Item(BaseItem):
    attributes = ListType(ModelType(Attribute, required=True))
    unit = ModelType(Unit)


class Organization(Model):
    """An organization."""
    name = StringType(required=True)
    name_en = StringType()
    name_ru = StringType()
    identifier = ModelType(Identifier, required=True)
    additionalIdentifiers = ListType(ModelType(Identifier))
    additionalContactPoints = ListType(ModelType(ContactPoint, required=True), required=False)
    address = ModelType(Address)
    signerInfo = ModelType(SignerInfo)


class PostContract(BasePostContract):
    """
    Model only for auto-creating contract
    """

    @serializable
    def status(self):
        return "pending"

    amountPaid = ModelType(AmountPaid)
    contractTemplateName = StringType()
    items = ListType(ModelType(Item, required=True))
    buyer = ModelType(
        Organization, required=True
    )
    value = ModelType(ContractValue)
    bid_owner = StringType(required=True)
    bid_token = StringType(required=True)


class PatchContract(BasePatchContract):
    status = StringType(choices=["pending", "terminated", "active", "cancelled"])
    items = ListType(ModelType(Item, required=True), min_size=1)
    terminationDetails = StringType()
    amountPaid = ModelType(AmountPaid)
    value = ModelType(ContractValue)

    def validate_items(self, data, items):
        validate_item_unit_values(data, items)


class PatchContractPending(BasePatchContract):
    status = StringType(choices=["pending", "terminated", "active", "cancelled"])
    items = ListType(ModelType(Item, required=True), min_size=1)
    dateSigned = IsoDateTimeType()
    contractNumber = StringType()
    value = ModelType(ContractValue)

    def validate_items(self, data, items):
        validate_item_unit_values(data, items)


class AdministratorPatchContract(Model):
    contractNumber = StringType()
    status = StringType(choices=["pending", "pending.winner-signing", "terminated", "active", "cancelled"])
    suppliers = ListType(ModelType(Organization, required=True), min_size=1, max_size=1)
    buyer = ModelType(Organization)
    mode = StringType(choices=["test"])


class Contract(BaseContract):
    status = StringType(choices=["pending", "pending.winner-signing", "terminated", "active", "cancelled"])
    buyer = ModelType(
        Organization, required=True
    )
    suppliers = ListType(ModelType(Organization, required=True), min_size=1, max_size=1)
    items = ListType(ModelType(Item, required=True), required=False, min_size=1, validators=[validate_items_uniq])
    contractTemplateName = StringType()
    value = ModelType(ContractValue)

    bid_owner = StringType(required=True)
    bid_token = StringType(required=True)
