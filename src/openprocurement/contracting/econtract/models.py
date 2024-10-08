from schematics.types import StringType
from schematics.types.compound import ModelType

from openprocurement.api.procedure.types import IsoDateTimeType, ListType
from openprocurement.contracting.core.procedure.models.contract import (
    BaseContract,
    BasePostContract,
)
from openprocurement.contracting.core.procedure.models.organization import (
    ProcuringEntity,
)
from openprocurement.contracting.econtract.procedure.models.contract import (
    validate_items_uniq,
)
from openprocurement.contracting.econtract.procedure.models.item import Item
from openprocurement.contracting.econtract.procedure.models.organization import (
    Organization,
)


class PostContract(BasePostContract):
    status = StringType(choices=["terminated", "active"], default="active")
    dateSigned = IsoDateTimeType()
    procuringEntity = ModelType(ProcuringEntity, required=True)


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
    buyer = ModelType(Organization, required=True)
    procuringEntity = ModelType(
        ProcuringEntity, required=True
    )  # The entity managing the procurement, which may be different from the buyer who is paying / using the items being procured.
    suppliers = ListType(ModelType(Organization, required=True), min_size=1, max_size=1)
    items = ListType(
        ModelType(Item, required=True),
        required=False,
        min_size=1,
        validators=[validate_items_uniq],
    )
    contractTemplateName = StringType()

    bid_owner = StringType(required=True)
    bid_token = StringType(required=True)
