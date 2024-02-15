from schematics.types import StringType

from openprocurement.api.procedure.models.organization import (
    Organization as BaseOrganization,
)
from openprocurement.api.procedure.types import ListType, ModelType
from openprocurement.tender.openuadefense.constants import DEFENSE_KINDS
from openprocurement.tender.openuadefense.procedure.models.contact import ContactPoint


class Organization(BaseOrganization):
    contactPoint = ModelType(ContactPoint, required=True)
    additionalContactPoints = ListType(ModelType(ContactPoint, required=True))


class ProcuringEntity(Organization):
    kind = StringType(choices=DEFENSE_KINDS, required=True)
