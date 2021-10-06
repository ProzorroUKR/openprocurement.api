from openprocurement.api.constants import SCALE_CODES
from openprocurement.api.models import Organization as BaseOrganization
from openprocurement.tender.core.models import PROCURING_ENTITY_KINDS
from openprocurement.tender.cfaselectionua.models.submodels.contactpoint import ContactPoint
from schematics.types import StringType
from schematics.types.compound import ModelType
from openprocurement.api.roles import RolesFromCsv
from openprocurement.api.models import ListType


class BusinessOrganization(BaseOrganization):
    scale = StringType(choices=SCALE_CODES)


class Organization(BaseOrganization):
    """An organization."""

    contactPoint = ModelType(ContactPoint)

    def validate_telephone(self, data, value):
        pass


class ProcuringEntity(Organization):
    """An organization."""

    class Options:
        roles = RolesFromCsv("ProcuringEntity.csv", relative_to=__file__)

    kind = StringType(choices=PROCURING_ENTITY_KINDS)
    additionalContactPoints = ListType(ModelType(ContactPoint, required=True), required=False)
