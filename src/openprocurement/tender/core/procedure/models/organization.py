from openprocurement.api.context import get_now
from openprocurement.tender.core.procedure.context import get_tender
from openprocurement.tender.core.procedure.models.contact import ContactPoint, PostContactPoint, PatchContactPoint
from openprocurement.tender.core.procedure.models.address import Address, PatchAddress, PostAddress
from openprocurement.tender.core.procedure.models.identifier import Identifier, PatchIdentifier
from openprocurement.tender.core.procedure.models.base import ModelType
from openprocurement.api.models import ListType, Model, MD5Type
from openprocurement.api.utils import get_first_revision_date
from openprocurement.api.constants import ORGANIZATION_SCALE_FROM, SCALE_CODES
from schematics.types import StringType, BaseType
from schematics.validate import ValidationError
from uuid import uuid4


PROCURING_ENTITY_KINDS = ("authority", "central", "defense", "general", "other", "social", "special")


class PatchOrganization(Model):  # TODO: remove Post, Patch models
    name = StringType()
    name_en = StringType()
    name_ru = StringType()
    identifier = ModelType(PatchIdentifier, name="Identifier")
    additionalIdentifiers = ListType(ModelType(PatchIdentifier))
    address = ModelType(PatchAddress)
    contactPoint = ModelType(PatchContactPoint)


class PostOrganization(PatchOrganization):
    name = StringType(required=True)
    identifier = ModelType(Identifier, required=True)
    additionalIdentifiers = ListType(ModelType(Identifier))
    address = ModelType(PostAddress, required=True)
    contactPoint = ModelType(PostContactPoint, required=True)


class PatchBusinessOrganization(PatchOrganization):
    scale = StringType(choices=SCALE_CODES)


class PostBusinessOrganization(PostOrganization, PatchBusinessOrganization):
    def validate_scale(self, data, value):
        tender = get_tender()
        validation_date = get_first_revision_date(tender, default=get_now())
        if validation_date >= ORGANIZATION_SCALE_FROM and value is None:
            raise ValidationError(BaseType.MESSAGES["required"])


class BusinessOrganization(PostBusinessOrganization):
    pass


class ContactLessBusinessOrganization(BusinessOrganization):
    contactPoint = ModelType(PostContactPoint)


class BaseOrganization(Model):
    id = MD5Type(default=lambda: uuid4().hex)
    name = StringType(required=True)
    name_en = StringType()
    name_ru = StringType()
    identifier = ModelType(Identifier, required=True)
    address = ModelType(Address)
    kind = StringType(choices=PROCURING_ENTITY_KINDS)


class Organization(Model):
    name = StringType(required=True)
    name_en = StringType()
    name_ru = StringType()
    identifier = ModelType(Identifier, required=True)
    additionalIdentifiers = ListType(ModelType(Identifier))
    address = ModelType(Address, required=True)
    contactPoint = ModelType(ContactPoint, required=True)
    additionalContactPoints = ListType(ModelType(ContactPoint, required=True))


class ProcuringEntity(Organization):
    kind = StringType(choices=PROCURING_ENTITY_KINDS, required=True)
