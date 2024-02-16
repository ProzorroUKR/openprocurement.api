from decimal import Decimal


def to_decimal(fraction):
    return Decimal(fraction.numerator) / Decimal(fraction.denominator)


def get_bid_identifier(bid):
    identifier = bid["tenderers"][0]["identifier"]
    return identifier["scheme"], identifier["id"]


def all_bids_values(tender, identifier):
    """
    :param tender:
    :param identifier: a tuple (identifier.scheme, identifier.id)
    :return: every lotValue for a specified (identifier.scheme, identifier.id)
    """
    for every_bid in tender["bids"]:
        if get_bid_identifier(every_bid) == identifier:
            yield from every_bid["lotValues"]
