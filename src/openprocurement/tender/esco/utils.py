# -*- coding: utf-8 -*-
from decimal import Decimal


def to_decimal(fraction):
    return Decimal(fraction.numerator) / Decimal(fraction.denominator)
