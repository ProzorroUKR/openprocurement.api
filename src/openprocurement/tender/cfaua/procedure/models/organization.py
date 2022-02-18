from openprocurement.tender.core.procedure.models.organization import Organization as BaseOrganization
from openprocurement.tender.cfaua.constants import CFA_UA_KINDS
from openprocurement.tender.cfaua.procedure.models.contact import ContactPoint
from openprocurement.tender.core.procedure.models.base import ModelType
from openprocurement.api.models import ListType
from schematics.types import StringType


class Organization(BaseOrganization):
    contactPoint = ModelType(ContactPoint, required=True)
    additionalContactPoints = ListType(ModelType(ContactPoint, required=True))


class ProcuringEntity(Organization):
    kind = StringType(choices=CFA_UA_KINDS, required=True)
