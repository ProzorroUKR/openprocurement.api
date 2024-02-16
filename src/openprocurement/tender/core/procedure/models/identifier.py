from schematics.types import BaseType, StringType

from openprocurement.api.constants import ORA_CODES
from openprocurement.api.procedure.models.identifier import Identifier


class PatchIdentifier(Identifier):
    scheme = StringType(
        choices=ORA_CODES
    )  # The scheme that holds the unique identifiers used to identify the item being identified.
    id = BaseType()  # The identifier of the organization in the selected scheme.


class LegislationIdentifier(Identifier):
    scheme = StringType()
