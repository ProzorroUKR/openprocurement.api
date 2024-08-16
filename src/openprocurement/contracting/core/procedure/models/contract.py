from uuid import uuid4

from schematics.types import BaseType, BooleanType, StringType
from schematics.types.compound import ModelType
from schematics.types.serializable import serializable

from openprocurement.api.procedure.models.base import Model
from openprocurement.api.procedure.models.period import Period
from openprocurement.api.procedure.models.value import ContractValue
from openprocurement.api.procedure.types import IsoDateTimeType, ListType
from openprocurement.api.validation import validate_items_uniq
from openprocurement.contracting.core.procedure.models.change import Change
from openprocurement.contracting.core.procedure.models.document import Document
from openprocurement.contracting.core.procedure.models.implementation import (
    Implementation,
)
from openprocurement.contracting.core.procedure.models.item import Item
from openprocurement.contracting.core.procedure.models.organization import (
    BusinessOrganization,
)
from openprocurement.contracting.core.procedure.models.value import AmountPaid


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
    implementation = ModelType(Implementation)
    status = StringType(choices=["terminated", "active"])
    period = ModelType(Period)
    value = ModelType(ContractValue)
    items = ListType(ModelType(Item, required=True), min_size=1)


class BaseContract(Model):
    """Contract"""

    _id = StringType(deserialize_from=['id', 'doc_id'])
    _rev = StringType()
    doc_type = StringType()
    public_modified = BaseType()

    buyerID = StringType()
    awardID = StringType()
    contractID = StringType()
    contractNumber = StringType()
    title = StringType()  # Contract title
    title_en = StringType()
    title_ru = StringType()
    description = StringType()  # Contract description
    description_en = StringType()
    description_ru = StringType()
    dateSigned = IsoDateTimeType()
    date = IsoDateTimeType()

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
    period = ModelType(Period)
    suppliers = ListType(ModelType(BusinessOrganization, required=True), min_size=1, max_size=1)
    changes = ListType(ModelType(Change, required=True))
    terminationDetails = StringType()
    implementation = ModelType(Implementation)
    is_masked = BooleanType()

    documents = ListType(ModelType(Document, required=True))
    amountPaid = ModelType(AmountPaid)
    value = ModelType(ContractValue)

    bid_owner = StringType()
    bid_token = StringType()

    revisions = BaseType()

    config = BaseType()

    _attachments = BaseType()  # deprecated

    @serializable(serialized_name="amountPaid", serialize_when_none=False, type=ModelType(AmountPaid))
    def contract_amountPaid(self):
        if self.amountPaid:
            self.amountPaid.currency = self.value.currency if self.value else self.amountPaid.currency
            if self.amountPaid.valueAddedTaxIncluded is None:
                self.amountPaid.valueAddedTaxIncluded = self.value.valueAddedTaxIncluded
            return self.amountPaid
