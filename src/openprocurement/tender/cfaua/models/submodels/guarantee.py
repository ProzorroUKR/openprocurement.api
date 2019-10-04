# -*- coding: utf-8 -*-
from decimal import Decimal
from openprocurement.api.models import DecimalType, Guarantee as BaseGuarantee


class Guarantee(BaseGuarantee):
    amount = DecimalType(required=True, precision=-2, min_value=Decimal("0.0"))  # Amount as a number.
