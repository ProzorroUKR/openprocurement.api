from openprocurement.api.models import Model, schematics_embedded_role, schematics_default_role, ListType, Address
from openprocurement.tender.cfaselectionua.models.submodels.contactpoint import ContactPoint
from openprocurement.api.models import Identifier

from schematics.transforms import blacklist
from schematics.types import StringType
from schematics.types.compound import ModelType


class Organization(Model):
    """An organization."""
    class Options:
        roles = {
            'embedded': schematics_embedded_role,
            'view': schematics_default_role,
        }

    name = StringType(required=True)
    name_en = StringType()
    name_ru = StringType()
    identifier = ModelType(Identifier, required=True)
    additionalIdentifiers = ListType(ModelType(Identifier))
    address = ModelType(Address, required=True)
    contactPoint = ModelType(ContactPoint, required=True)


class ProcuringEntity(Organization):
    """An organization."""
    class Options:
        roles = {
            'embedded': schematics_embedded_role,
            'view': schematics_default_role,
            'edit_active.enquiries': schematics_default_role + blacklist("kind"),
            'edit_active.tendering': schematics_default_role + blacklist("kind"),
        }

    kind = StringType(choices=['general', 'special', 'defense', 'other'])
