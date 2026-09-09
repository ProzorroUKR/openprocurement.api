from schematics.exceptions import ValidationError
from schematics.types import BooleanType, MD5Type, StringType

from openprocurement.api.procedure.context import get_tender
from openprocurement.api.procedure.models.value import Value
from openprocurement.api.procedure.types import ListType, ModelType
from openprocurement.tender.core.procedure.models.award import Award, PatchAward, PostAward
from openprocurement.tender.core.procedure.models.organization import ContactLessSupplier, Supplier


class LimitedAwardValue(Value):
    valueAddedTaxIncluded = BooleanType(required=True, default=lambda: get_tender()["value"]["valueAddedTaxIncluded"])
    currency = StringType(
        required=True,
        max_length=3,
        min_length=3,
        default=lambda: get_tender()["value"]["currency"],
    )


class LimitedPostAward(PostAward):
    bid_id = MD5Type()  # awards are created by the buyer, there are no bids
    qualified = BooleanType()
    eligible = BooleanType()
    value = ModelType(LimitedAwardValue, required=True)
    weightedValue = ModelType(LimitedAwardValue)


class LimitedPatchAward(PatchAward):
    suppliers = ListType(ModelType(Supplier, required=True), min_size=1, max_size=1)
    value = ModelType(LimitedAwardValue)
    lotID = MD5Type()

    def validate_lotID(self, data, value):
        if value:
            tender = get_tender()
            if value not in tuple(lot["id"] for lot in tender.get("lots", "") if lot):
                raise ValidationError("lotID should be one of lots")


class LimitedAward(Award):
    bid_id = MD5Type()
    value = ModelType(LimitedAwardValue, required=True)
    weightedValue = ModelType(LimitedAwardValue)


class ReportingPostAward(LimitedPostAward):
    suppliers = ListType(
        ModelType(ContactLessSupplier, required=True),
        required=True,
        min_size=1,
        max_size=1,
    )
    value = ModelType(Value, required=True)


class ReportingPatchAward(LimitedPatchAward):
    suppliers = ListType(
        ModelType(ContactLessSupplier, required=True),
        min_size=1,
        max_size=1,
    )
    value = ModelType(Value)


class ReportingAward(LimitedAward):
    suppliers = ListType(
        ModelType(ContactLessSupplier, required=True),
        required=True,
        min_size=1,
        max_size=1,
    )
    value = ModelType(Value, required=True)
