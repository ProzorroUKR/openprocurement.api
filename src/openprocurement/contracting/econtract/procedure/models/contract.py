from schematics.exceptions import ValidationError
from schematics.types import StringType
from schematics.types.compound import ModelType
from schematics.types.serializable import serializable

from openprocurement.api.procedure.context import get_contract, get_tender
from openprocurement.api.procedure.models.base import Model
from openprocurement.api.procedure.models.value import ContractValue
from openprocurement.api.procedure.types import IsoDateTimeType, ListType
from openprocurement.api.validation import validate_items_uniq
from openprocurement.contracting.core.procedure.models.contract import (
    BaseContract,
    BasePatchContract,
    BasePostContract,
)
from openprocurement.contracting.core.procedure.models.value import AmountPaid
from openprocurement.contracting.econtract.procedure.models.document import Document
from openprocurement.contracting.econtract.procedure.models.item import Item
from openprocurement.contracting.econtract.procedure.models.organization import (
    Buyer,
    Supplier,
)


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
    buyer = ModelType(Buyer, required=True)
    suppliers = ListType(ModelType(Supplier, required=True), min_size=1, max_size=1)
    value = ModelType(ContractValue)


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


class Contract(BaseContract):
    status = StringType(
        choices=[
            "pending",
            "pending.winner-signing",
            "terminated",
            "active",
            "cancelled",
        ]
    )
    buyer = ModelType(Buyer, required=True)
    suppliers = ListType(ModelType(Supplier, required=True), min_size=1, max_size=1)
    items = ListType(
        ModelType(Item, required=True),
        required=False,
        min_size=1,
        validators=[validate_items_uniq],
    )
    contractTemplateName = StringType()
    value = ModelType(ContractValue)
    documents = ListType(ModelType(Document, required=True))


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
