from openprocurement.api.procedure.models.address import Address


class FullAddress(Address):
    streetAddress: str
    locality: str
    region: str
    postalCode: str
