from decimal import Decimal

from schematics.types.compound import ListType, ModelType

from openprocurement.api.procedure.types import DecimalType
from openprocurement.api.validation import validate_uniq_value
from openprocurement.tender.core.procedure.models.feature import Feature as BaseFeature
from openprocurement.tender.core.procedure.models.feature import (
    FeatureValue as BaseFeatureValue,
)


class FeatureValue(BaseFeatureValue):
    value = DecimalType(required=True, min_value=Decimal("0.0"), max_value=Decimal("0.3"))


class Feature(BaseFeature):
    enum = ListType(
        ModelType(FeatureValue, required=True),
        min_size=1,
        validators=[validate_uniq_value],
    )
