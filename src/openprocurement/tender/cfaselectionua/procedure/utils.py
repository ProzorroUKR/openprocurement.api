from decimal import Decimal


DECIMAL_COMPARE_ACCURACY = Decimal("1e-12")


def equals_decimal_and_corrupted(value, corrupted_value):
    """
    Ex. value is Decimal('0.1'),
    tender.feature.enum values can be like
    '0.050000000000000002776', '0.10000000000000000555', '0.14999999999999999445'
    how do I check this ?
    :param value:
    :param corrupted_value:
    :return:
    """
    corrupted_value = Decimal(corrupted_value)
    return value == corrupted_value or value == corrupted_value.quantize(DECIMAL_COMPARE_ACCURACY)
