from decimal import Decimal

from schematics.types.compound import ModelType

from openprocurement.api.procedure.types import DecimalType, ListType
from openprocurement.api.procedure.validation import validate_values_uniq
from openprocurement.tender.core.procedure.models.feature import Feature as BaseFeature
from openprocurement.tender.core.procedure.models.feature import (
    FeatureValue as BaseFeatureValue,
)


class FeatureValue(BaseFeatureValue):
    value = DecimalType(required=True, precision=-2, min_value=Decimal("0.0"), max_value=Decimal("0.3"))


class Feature(BaseFeature):
    enum = ListType(ModelType(FeatureValue, required=True), default=list, min_size=1, validators=[validate_values_uniq])
