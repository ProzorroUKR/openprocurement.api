# -*- coding: utf-8 -*-
from decimal import Decimal
from openprocurement.api.utils import get_now


def request_get_now(request):
    return get_now()

def to_decimal(fraction):
    return Decimal(fraction.numerator) / Decimal(fraction.denominator)
