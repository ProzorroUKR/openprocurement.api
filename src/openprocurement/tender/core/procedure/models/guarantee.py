from schematics.exceptions import ValidationError
from schematics.types import BooleanType, FloatType, StringType

from openprocurement.api.constants import CURRENCIES
from openprocurement.api.procedure.models.base import Model
from openprocurement.api.procedure.models.guarantee import Guarantee as BaseGuarantee
from openprocurement.api.procedure.types import DecimalType


class Guarantee(BaseGuarantee):
    pass


class PostGuarantee(Guarantee):
    currency = StringType(required=True, default="UAH", max_length=3, min_length=3)


class EstimatedValue(Model):
    """Estimated lot value.

    Amount is not required.
    """

    amount = FloatType(required=False, min_value=0)
    currency = StringType(required=True, default="UAH", max_length=3, min_length=3)
    valueAddedTaxIncluded = BooleanType(required=True)

    def validate_currency(self, estimated_value, currency):
        if currency not in CURRENCIES:
            raise ValidationError(f"Currency must be only {', '.join(CURRENCIES)}.")


class PostEstimatedValue(EstimatedValue):
    valueAddedTaxIncluded = BooleanType(required=True, default=True)


class Value(Guarantee):
    valueAddedTaxIncluded = BooleanType(required=True)


class PostValue(PostGuarantee, Value):
    valueAddedTaxIncluded = BooleanType(required=True, default=True)


class WeightedValue(PostValue):
    amount = DecimalType(required=True, precision=-2)
    denominator = FloatType()
    addition = DecimalType(precision=-2)
