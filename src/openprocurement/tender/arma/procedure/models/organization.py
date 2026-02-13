from schematics.types import StringType

from openprocurement.api.procedure.models.organization import (
    PROCURING_ENTITY_KIND_CHOICES,
)
from openprocurement.api.procedure.models.organization import (
    Organization as BaseOrganization,
)
from openprocurement.api.procedure.models.signer_info import SignerInfo
from openprocurement.api.procedure.types import ListType, ModelType
from openprocurement.tender.arma.procedure.models.contact import ContactPoint
from openprocurement.tender.arma.procedure.models.identifier import Identifier


class Organization(BaseOrganization):
    name_en = StringType(required=False, min_length=1)
    identifier = ModelType(Identifier, required=True)
    contactPoint = ModelType(ContactPoint, required=True)
    additionalContactPoints = ListType(ModelType(ContactPoint, required=True))


class ProcuringEntity(Organization):
    kind = StringType(choices=PROCURING_ENTITY_KIND_CHOICES, required=True)
    signerInfo = ModelType(SignerInfo)
    contract_owner = StringType()
