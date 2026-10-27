from uuid import uuid4

from schematics.types import MD5Type, StringType

from openprocurement.api.procedure.models.address import Address
from openprocurement.api.procedure.models.base import Model
from openprocurement.api.procedure.models.contact import ContactPoint
from openprocurement.api.procedure.models.identifier import Identifier
from openprocurement.api.procedure.models.organization import (
    PROCURING_ENTITY_KIND_CHOICES,
)
from openprocurement.api.procedure.models.signer_info import SignerInfo
from openprocurement.api.procedure.types import ModelType


class BaseOrganization(Model):
    id = MD5Type(default=lambda: uuid4().hex)
    name = StringType(required=True)
    name_en = StringType()
    name_ru = StringType()
    identifier = ModelType(Identifier, required=True)
    address = ModelType(Address)
    kind = StringType(choices=PROCURING_ENTITY_KIND_CHOICES)


class ProcuringEntity(BaseOrganization):
    signerInfo = ModelType(SignerInfo)


class BuyerOrganization(ProcuringEntity):
    contactPoint = ModelType(ContactPoint)
