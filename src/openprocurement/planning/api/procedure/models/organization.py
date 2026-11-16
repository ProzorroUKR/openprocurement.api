from uuid import uuid4

from pydantic import Field

from openprocurement.api.procedure.models.address import Address
from openprocurement.api.procedure.models.base import Model
from openprocurement.api.procedure.models.contact import ContactPoint
from openprocurement.api.procedure.models.identifier import Identifier
from openprocurement.api.procedure.models.organization import (
    ProcuringEntityKind,
)
from openprocurement.api.procedure.models.signer_info import SignerInfo
from openprocurement.api.procedure.types import MD5


class BaseOrganization(Model):
    id: MD5 = Field(default_factory=lambda: uuid4().hex)
    name: str
    name_en: str | None = None
    name_ru: str | None = None
    identifier: Identifier
    address: Address | None = None
    kind: ProcuringEntityKind | None = None


class ProcuringEntity(BaseOrganization):
    signerInfo: SignerInfo | None = None


class BuyerOrganization(ProcuringEntity):
    contactPoint: ContactPoint | None = None
