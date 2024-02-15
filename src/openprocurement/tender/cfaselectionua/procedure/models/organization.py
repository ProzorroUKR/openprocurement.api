from schematics.types import StringType

from openprocurement.api.constants import SCALE_CODES
from openprocurement.api.procedure.models.organization import (
    Organization as BaseOrganization,
)
from openprocurement.api.procedure.types import ListType, ModelType
from openprocurement.tender.cfaselectionua.constants import CFA_SELECTION_KINDS
from openprocurement.tender.cfaselectionua.procedure.models.address import Address
from openprocurement.tender.cfaselectionua.procedure.models.contact import ContactPoint


class BusinessOrganization(BaseOrganization):
    scale = StringType(choices=SCALE_CODES)
    address = ModelType(Address, required=True)


class Organization(BaseOrganization):
    contactPoint = ModelType(ContactPoint, required=True)
    additionalContactPoints = ListType(ModelType(ContactPoint, required=True))
    address = ModelType(Address, required=True)


class ProcuringEntity(Organization):
    kind = StringType(choices=CFA_SELECTION_KINDS, required=True)
