from uuid import uuid4

from schematics.types import StringType, BaseType, BooleanType
from schematics.types.compound import ModelType
from schematics.types.serializable import serializable

from openprocurement.api.constants import SCALE_CODES
from openprocurement.api.models import Period, BaseContract as CommonBaseContract, ContractValue, PROCURING_ENTITY_KINDS
from openprocurement.api.models import Organization as BaseOrganization
from openprocurement.api.models import ContactPoint as BaseContactPoint
from openprocurement.api.models import CPVClassification as BaseCPVClassification
from openprocurement.api.models import Item as BaseItem
from openprocurement.api.models import Address as BaseAddress
from openprocurement.api.models import AdditionalClassification as BaseAdditionalClassification
from openprocurement.api.models import Model, ListType, IsoDateTimeType
from openprocurement.api.validation import validate_items_uniq
from openprocurement.api.models import Unit as BaseUnit

from openprocurement.contracting.core.procedure.models.change import Change
from openprocurement.contracting.core.procedure.models.transaction import Transaction
from openprocurement.contracting.core.procedure.models.document import Document


class ContactPoint(BaseContactPoint):
    availableLanguage = StringType()

    def validate_telephone(self, data, value):
        pass


class Address(BaseAddress):
    def validate_countryName(self, data, value):
        pass

    def validate_region(self, data, value):
        pass


class Organization(BaseOrganization):
    """An organization."""

    contactPoint = ModelType(ContactPoint, required=True)
    additionalContactPoints = ListType(ModelType(ContactPoint, required=True), required=False)
    address = ModelType(Address, required=True)


class BusinessOrganization(Organization):
    """An organization."""
    scale = StringType(choices=SCALE_CODES)
    contactPoint = ModelType(ContactPoint)


class ProcuringEntity(Organization):
    """An organization."""

    kind = StringType(choices=PROCURING_ENTITY_KINDS)
    contactPoint = ModelType(ContactPoint)


class CPVClassification(BaseCPVClassification):
    def validate_scheme(self, data, scheme):
        pass


class AdditionalClassification(BaseAdditionalClassification):
    def validate_id(self, data, code):
        pass


class UnitForContracting(BaseUnit):
    def validate_code(self, data, value):
        pass


class Item(BaseItem):

    classification = ModelType(CPVClassification, required=True)
    additionalClassifications = ListType(ModelType(AdditionalClassification, required=True), default=list())
    unit = ModelType(UnitForContracting)
    deliveryAddress = ModelType(Address)


class Implementation(Model):
    transactions = ListType(ModelType(Transaction), default=list())


class AmountPaid(ContractValue):
    valueAddedTaxIncluded = BooleanType()


class BasePostContract(Model):
    @serializable
    def owner_token(self):
        return uuid4().hex

    @serializable
    def transfer_token(self):
        return uuid4().hex

    id = StringType()
    _id = StringType(deserialize_from=['id', 'doc_id'])
    awardID = StringType()
    contractID = StringType()
    buyerID = StringType()
    contractNumber = StringType()

    title = StringType()
    title_en = StringType()
    title_ru = StringType()
    description = StringType()
    description_en = StringType()
    description_ru = StringType()

    period = ModelType(Period)
    value = ModelType(ContractValue)

    items = ListType(ModelType(Item, required=True))
    documents = ListType(ModelType(Document, required=True))
    suppliers = ListType(ModelType(BusinessOrganization), min_size=1, max_size=1)

    owner = StringType()
    tender_token = StringType(required=True)
    tender_id = StringType(required=True)
    mode = StringType(choices=["test"])


class BasePatchContract(Model):
    title = StringType()
    title_en = StringType()
    title_ru = StringType()
    description = StringType()
    description_en = StringType()
    description_ru = StringType()
    terminationDetails = StringType()
    implementation = ModelType(Implementation)
    status = StringType(choices=["terminated", "active"])
    period = ModelType(Period)
    value = ModelType(ContractValue)
    items = ListType(ModelType(Item, required=True), min_size=1)
    amountPaid = ModelType(AmountPaid)


class BaseContract(CommonBaseContract):
    """ Contract """
    _id = StringType(deserialize_from=['id', 'doc_id'])
    _rev = StringType()
    public_modified = BaseType()

    revisions = BaseType()

    dateModified = IsoDateTimeType()
    dateCreated = IsoDateTimeType()
    items = ListType(ModelType(Item, required=True), required=False, min_size=1, validators=[validate_items_uniq])
    tender_token = StringType(required=True)
    tender_id = StringType(required=True)
    owner_token = StringType(default=lambda: uuid4().hex)
    transfer_token = StringType(default=lambda: uuid4().hex)
    owner = StringType()
    mode = StringType(choices=["test"])
    status = StringType(choices=["terminated", "active"], default="active")
    suppliers = ListType(ModelType(BusinessOrganization, required=True), min_size=1, max_size=1)
    changes = ListType(ModelType(Change, required=True))
    terminationDetails = StringType()
    implementation = ModelType(Implementation)
    is_masked = BooleanType()

    documents = ListType(ModelType(Document, required=True))
    amountPaid = ModelType(AmountPaid)
    value = ModelType(ContractValue)

    _attachments = BaseType()  # deprecated

    @serializable(serialized_name="amountPaid", serialize_when_none=False, type=ModelType(AmountPaid))
    def contract_amountPaid(self):
        if self.amountPaid:
            self.amountPaid.currency = self.value.currency if self.value else self.amountPaid.currency
            if self.amountPaid.valueAddedTaxIncluded is None:
                self.amountPaid.valueAddedTaxIncluded = self.value.valueAddedTaxIncluded
            return self.amountPaid
