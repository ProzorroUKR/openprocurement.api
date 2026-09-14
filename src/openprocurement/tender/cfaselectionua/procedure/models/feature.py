from decimal import Decimal

from schematics.types.compound import ModelType

from openprocurement.api.procedure.types import DecimalType, ListType
from openprocurement.api.validation import validate_uniq_value
from openprocurement.tender.core.procedure.models.feature import Feature, FeatureValue


class CFASelectionFeatureValue(FeatureValue):
    value = DecimalType(required=True, min_value=Decimal("0.0"), max_value=Decimal("0.3"))


class CFASelectionFeature(Feature):
    enum = ListType(
        ModelType(CFASelectionFeatureValue, required=True),
        min_size=1,
        validators=[validate_uniq_value],
    )
