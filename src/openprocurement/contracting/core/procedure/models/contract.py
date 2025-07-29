from uuid import uuid4

from schematics.exceptions import ValidationError
from schematics.types import BaseType, BooleanType, StringType
from schematics.types.compound import ModelType
from schematics.types.serializable import serializable

from openprocurement.api.procedure.context import get_contract, get_tender
from openprocurement.api.procedure.models.base import Model
from openprocurement.api.procedure.models.period import Period
from openprocurement.api.procedure.models.value import ContractValue
from openprocurement.api.procedure.types import IsoDateTimeType, ListType
from openprocurement.api.validation import validate_items_uniq
from openprocurement.contracting.core.procedure.models.access import AccessDetails
from openprocurement.contracting.core.procedure.models.change import Change
from openprocurement.contracting.core.procedure.models.document import Document
from openprocurement.contracting.core.procedure.models.implementation import (
    Implementation,
)
from openprocurement.contracting.core.procedure.models.item import Item
from openprocurement.contracting.core.procedure.models.organization import (
    Buyer,
    Supplier,
)
from openprocurement.contracting.core.procedure.models.value import AmountPaid


class PostContract(Model):
    """
    Model only for auto-creating contract
    """

    @serializable
    def transfer_token(self):
        return uuid4().hex

    @serializable
    def status(self):
        return "pending"

    id = StringType()
    _id = StringType(deserialize_from=["id", "doc_id"])
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
    buyer = ModelType(Buyer, required=True)
    suppliers = ListType(ModelType(Supplier), min_size=1, max_size=1)

    owner = StringType()
    access = ListType(ModelType(AccessDetails, required=True))
    tender_id = StringType(required=True)
    mode = StringType(choices=["test"])

    amountPaid = ModelType(AmountPaid)
    contractTemplateName = StringType()


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


class Contract(Model):
    """Contract"""

    _id = StringType(deserialize_from=["id", "doc_id"])
    _rev = StringType()
    doc_type = StringType()
    public_modified = BaseType()
    public_ts = BaseType()

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
    items = ListType(
        ModelType(Item, required=True),
        required=False,
        min_size=1,
        validators=[validate_items_uniq],
    )
    tender_token = StringType()  # deprecated
    tender_id = StringType(required=True)
    owner_token = StringType()  # deprecated
    transfer_token = StringType(default=lambda: uuid4().hex)
    owner = StringType()
    mode = StringType(choices=["test"])
    status = StringType(
        choices=[
            "pending",
            "pending.winner-signing",
            "terminated",
            "active",
            "cancelled",
        ]
    )
    period = ModelType(Period)
    buyer = ModelType(Buyer, required=True)
    suppliers = ListType(ModelType(Supplier, required=True), min_size=1, max_size=1)
    contractTemplateName = StringType()
    changes = ListType(ModelType(Change, required=True))
    terminationDetails = StringType()
    implementation = ModelType(Implementation)
    is_masked = BooleanType()

    documents = ListType(ModelType(Document, required=True))
    amountPaid = ModelType(AmountPaid)
    value = ModelType(ContractValue)

    bid_owner = StringType()  # deprecated
    bid_token = StringType()  # deprecated

    access = ListType(ModelType(AccessDetails, required=True))

    revisions = BaseType()

    config = BaseType()

    _attachments = BaseType()  # deprecated

    @serializable(
        serialized_name="amountPaid",
        serialize_when_none=False,
        type=ModelType(AmountPaid),
    )
    def contract_amountPaid(self):
        if self.amountPaid:
            self.amountPaid.currency = self.value.currency if self.value else self.amountPaid.currency
            if self.amountPaid.valueAddedTaxIncluded is None:
                self.amountPaid.valueAddedTaxIncluded = self.value.valueAddedTaxIncluded
            return self.amountPaid


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
    status = StringType(
        choices=[
            "pending",
            "pending.winner-signing",
            "terminated",
            "active",
            "cancelled",
        ]
    )
    suppliers = ListType(ModelType(Supplier, required=True), min_size=1, max_size=1)
    buyer = ModelType(Buyer)
    mode = StringType(choices=["test"])


def validate_item_unit_values(data, items):
    base_value = data.get("value")
    if base_value is None:
        base_value = (get_contract() or {}).get("value")
    if base_value and items:
        for item in items:
            item_value = (item.get("unit") or {}).get("value")
            if item_value:
                if (
                    get_tender()["config"]["valueCurrencyEquality"] is True
                    and item_value["currency"] != base_value["currency"]
                ):
                    raise ValidationError(f"Value mismatch. Expected: currency {base_value['currency']}")
