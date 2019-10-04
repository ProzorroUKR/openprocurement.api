# -*- coding: utf-8 -*-
from decimal import Decimal
from openprocurement.api.models import DecimalType, ModelType, ListType
from openprocurement.tender.core.models import (
    validate_values_uniq,
    Feature as BaseFeature,
    FeatureValue as BaseFeatureValue,
)


class FeatureValue(BaseFeatureValue):
    value = DecimalType(required=True, precision=-2, min_value=Decimal("0.0"), max_value=Decimal("0.3"))


class Feature(BaseFeature):
    enum = ListType(
        ModelType(FeatureValue, required=True), default=list(), min_size=1, validators=[validate_values_uniq]
    )
