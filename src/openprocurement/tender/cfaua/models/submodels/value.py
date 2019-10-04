# -*- coding: utf-8 -*-
from decimal import Decimal
from openprocurement.api.models import DecimalType, Value as BaseValue


class Value(BaseValue):
    amount = DecimalType(required=True, precision=-2, min_value=Decimal("0.0"))
