from openprocurement.api.models import Organization as BaseOrganization
from openprocurement.api.models import schematics_embedded_role, schematics_default_role
from openprocurement.tender.cfaselectionua.models.submodels.contactpoint import ContactPoint

from schematics.transforms import blacklist
from schematics.types import StringType
from schematics.types.compound import ModelType


class Organization(BaseOrganization):
    """An organization."""
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
