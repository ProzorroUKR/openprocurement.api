from schematics.types import StringType

from openprocurement.api.procedure.models.organization import (
    Organization as BaseOrganization,
)
from openprocurement.api.procedure.models.signer_info import SignerInfo
from openprocurement.api.procedure.types import ListType, ModelType
from openprocurement.tender.openeu.constants import EU_PROCURING_ENTITY_KIND_CHOICES
from openprocurement.tender.openeu.procedure.models.contact import ContactPoint
from openprocurement.tender.openeu.procedure.models.identifier import Identifier


class Organization(BaseOrganization):
    name_en = StringType(required=True, min_length=1)
    identifier = ModelType(Identifier, required=True)
    contactPoint = ModelType(ContactPoint, required=True)
    additionalContactPoints = ListType(ModelType(ContactPoint, required=True))


class ProcuringEntity(Organization):
    kind = StringType(choices=EU_PROCURING_ENTITY_KIND_CHOICES, required=True)
    signerInfo = ModelType(SignerInfo)
