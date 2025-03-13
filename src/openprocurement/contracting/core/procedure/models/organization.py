from schematics.types import StringType
from schematics.types.compound import ModelType

from openprocurement.api.procedure.models.address import Address
from openprocurement.api.procedure.models.organization import (
    ORGANIZATION_SCALE_CHOICES,
    PROCURING_ENTITY_KIND_CHOICES,
)
from openprocurement.api.procedure.models.organization import (
    Organization as BaseOrganization,
)
from openprocurement.api.procedure.types import ListType
from openprocurement.contracting.core.procedure.models.contact import ContactPoint


class Organization(BaseOrganization):
    """An organization."""

    contactPoint = ModelType(ContactPoint, required=True)
    additionalContactPoints = ListType(ModelType(ContactPoint, required=True), required=False)
    address = ModelType(Address, required=True)


class BusinessOrganization(Organization):
    """An organization."""

    scale = StringType(choices=ORGANIZATION_SCALE_CHOICES)
    contactPoint = ModelType(ContactPoint)


class ProcuringEntity(Organization):
    """An organization."""

    kind = StringType(choices=PROCURING_ENTITY_KIND_CHOICES)
    contactPoint = ModelType(ContactPoint)
