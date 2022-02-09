from openprocurement.api.constants import ORA_CODES
from openprocurement.api.models import Model
from schematics.types import StringType, URLType, BaseType


class PatchIdentifier(Model):
    scheme = StringType(
        choices=ORA_CODES
    )  # The scheme that holds the unique identifiers used to identify the item being identified.
    id = BaseType()  # The identifier of the organization in the selected scheme.
    legalName = StringType()  # The legally registered name of the organization.
    legalName_en = StringType()
    legalName_ru = StringType()
    uri = URLType()  # A URI to identify the organization.


class Identifier(Model):
    scheme = StringType(choices=ORA_CODES, required=True)
    id = BaseType(required=True)
    legalName = StringType()
    legalName_en = StringType()
    legalName_ru = StringType()
    uri = URLType()


class LegislationIdentifier(Identifier):
    scheme = StringType()
