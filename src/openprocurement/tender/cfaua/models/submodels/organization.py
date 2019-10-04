from openprocurement.api.models import Model, schematics_embedded_role, schematics_default_role, ListType, Address
from openprocurement.tender.core.models import PROCURING_ENTITY_KINDS
from openprocurement.tender.cfaua.models.submodels.contactpoint import ContactPoint
from openprocurement.tender.cfaua.models.submodels.identifier import Identifier
from schematics.transforms import blacklist
from schematics.types import StringType
from schematics.types.compound import ModelType


class Organization(Model):
    """An organization."""

    class Options:
        roles = {"embedded": schematics_embedded_role, "view": schematics_default_role}

    name = StringType(required=True)
    name_en = StringType(required=True, min_length=1)
    name_ru = StringType()
    identifier = ModelType(Identifier, required=True)
    additionalIdentifiers = ListType(ModelType(Identifier, required=True))
    address = ModelType(Address, required=True)
    contactPoint = ModelType(ContactPoint, required=True)
    additionalContactPoints = ListType(ModelType(ContactPoint, required=True), required=False)


class ProcuringEntity(Organization):
    """An organization."""

    class Options:
        roles = {
            "embedded": schematics_embedded_role,
            "view": schematics_default_role,
            "edit_active.tendering": schematics_default_role + blacklist("kind"),
        }

    kind = StringType(choices=PROCURING_ENTITY_KINDS)
