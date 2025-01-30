from schematics.types import StringType
from schematics.types.compound import ModelType
from schematics.types.serializable import serializable

from openprocurement.api.procedure.models.base import Model
from openprocurement.api.procedure.models.value import ContractValue
from openprocurement.api.procedure.types import IsoDateTimeType, ListType
from openprocurement.api.validation import validate_items_uniq
from openprocurement.contracting.core.procedure.models.contract import (
    BaseContract,
    BasePatchContract,
    BasePostContract,
)
from openprocurement.contracting.core.procedure.models.milestone import (
    ContractMilestone,
)
from openprocurement.contracting.core.procedure.models.value import AmountPaid
from openprocurement.contracting.econtract.procedure.models.document import Document
from openprocurement.contracting.econtract.procedure.models.item import Item
from openprocurement.contracting.econtract.procedure.models.organization import (
    Buyer,
    Supplier,
)
from openprocurement.tender.core.procedure.models.contract import (
    validate_item_unit_values,
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
    milestones = ListType(ModelType(ContractMilestone, required=True))
    buyer = ModelType(Buyer, required=True)
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
    milestones = ListType(ModelType(ContractMilestone, required=True))
