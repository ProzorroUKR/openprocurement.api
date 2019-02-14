from openprocurement.api.models import Organization as BaseOrganization
from openprocurement.tender.cfaselectionua.models.submodels.contactpoint import ContactPoint
from schematics.types import StringType
from schematics.types.compound import ModelType
from openprocurement.api.roles import RolesFromCsv


class Organization(BaseOrganization):
    """An organization."""
    contactPoint = ModelType(ContactPoint)


class ProcuringEntity(Organization):
    """An organization."""

    class Options:
        roles = RolesFromCsv('ProcuringEntity.csv', relative_to=__file__)
    kind = StringType(choices=['general', 'special', 'defense', 'other'])
