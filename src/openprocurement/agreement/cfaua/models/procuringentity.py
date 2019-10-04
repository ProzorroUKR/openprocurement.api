from openprocurement.api.roles import RolesFromCsv
from schematics.types import StringType
from schematics.types.compound import ModelType
from openprocurement.tender.core.models import PROCURING_ENTITY_KINDS
from openprocurement.api.models import ListType, Organization

from openprocurement.agreement.cfaua.models.contactpoint import ContactPoint


class ProcuringEntity(Organization):
    """An organization."""

    class Options:
        # TODO: do we really need roles here
        roles = RolesFromCsv("ProcuringEntity.csv", relative_to=__file__)

    kind = StringType(choices=PROCURING_ENTITY_KINDS)
    contactPoint = ModelType(ContactPoint, required=True)
    additionalContactPoints = ListType(ModelType(ContactPoint, required=True), required=False)
