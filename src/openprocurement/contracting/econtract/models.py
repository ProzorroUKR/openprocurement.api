from schematics.types import StringType
from schematics.types.compound import ModelType

from openprocurement.contracting.api.models import Contract as BaseContract
from openprocurement.api.models import ListType
from openprocurement.contracting.econtract.procedure.models.contract import Organization, Item, validate_items_uniq


class Contract(BaseContract):
    status = StringType(choices=["pending", "pending.winner-signing", "terminated", "active", "cancelled"])
    buyer = ModelType(
        Organization, required=True
    )
    suppliers = ListType(ModelType(Organization, required=True), min_size=1, max_size=1)
    items = ListType(ModelType(Item, required=True), required=False, min_size=1, validators=[validate_items_uniq])
    contractTemplateName = StringType()

    bid_owner = StringType(required=True)
    bid_token = StringType(required=True)

