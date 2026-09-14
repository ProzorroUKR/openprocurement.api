from schematics.types import StringType

from openprocurement.api.procedure.models.address import Address
from openprocurement.api.procedure.models.organization import ORGANIZATION_SCALE_CHOICES
from openprocurement.api.procedure.models.organization import Organization as BaseOrganization
from openprocurement.api.procedure.types import ModelType


class CFASelectionBusinessOrganization(BaseOrganization):
    scale = StringType(choices=ORGANIZATION_SCALE_CHOICES)
    address = ModelType(Address, required=True)
