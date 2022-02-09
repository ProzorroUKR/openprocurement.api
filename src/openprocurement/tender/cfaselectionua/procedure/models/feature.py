from decimal import Decimal
from schematics.types.compound import ModelType, ListType
from openprocurement.api.models import DecimalType
from openprocurement.tender.core.procedure.models.feature import (
    Feature as BaseFeature,
    FeatureValue as BaseFeatureValue,
)
from openprocurement.framework.cfaua.validation import validate_values_uniq


class FeatureValue(BaseFeatureValue):
    value = DecimalType(required=True, min_value=Decimal("0.0"), max_value=Decimal("0.3"))


class Feature(BaseFeature):
    enum = ListType(
        ModelType(FeatureValue, required=True), min_size=1, validators=[validate_values_uniq]
    )
