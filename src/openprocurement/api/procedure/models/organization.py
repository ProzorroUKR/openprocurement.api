from schematics.types import StringType

from openprocurement.api.constants import SCALE_CODES
from openprocurement.api.procedure.models.base import Model
from openprocurement.api.procedure.types import ListType, ModelType
from openprocurement.api.procedure.models.identifier import Identifier
from openprocurement.api.procedure.models.address import Address
from openprocurement.api.procedure.models.contact import ContactPoint


PROCURING_ENTITY_KINDS = ("authority", "central", "defense", "general", "other", "social", "special")


class CommonOrganization(Model):
    name = StringType(required=True)
    name_en = StringType()
    name_ru = StringType()
    identifier = ModelType(Identifier, required=True)


class Organization(CommonOrganization):
    name = StringType(required=True)
    name_en = StringType()
    name_ru = StringType()
    identifier = ModelType(Identifier, required=True)
    additionalIdentifiers = ListType(ModelType(Identifier))
    address = ModelType(Address, required=True)
    contactPoint = ModelType(ContactPoint, required=True)
    additionalContactPoints = ListType(ModelType(ContactPoint, required=True))


class BusinessOrganization(Organization):
    scale = StringType(choices=SCALE_CODES, required=True)
