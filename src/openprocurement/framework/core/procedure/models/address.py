from schematics.types import StringType

from openprocurement.api.procedure.models.address import Address


class FullAddress(Address):
    streetAddress = StringType(required=True)
    locality = StringType(required=True)
    region = StringType(required=True)
    postalCode = StringType(required=True)
