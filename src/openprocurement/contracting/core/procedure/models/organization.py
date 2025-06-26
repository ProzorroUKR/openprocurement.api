from schematics.types import StringType
from schematics.types.compound import ModelType

from openprocurement.api.constants_env import VALIDATE_ADDRESS_FROM
from openprocurement.api.procedure.models.address import Address as BaseAddress
from openprocurement.api.procedure.models.base import Model
from openprocurement.api.procedure.models.identifier import Identifier
from openprocurement.api.procedure.models.organization import (
    ORGANIZATION_SCALE_CHOICES,
    PROCURING_ENTITY_KIND_CHOICES,
)
from openprocurement.api.procedure.models.signer_info import SignerInfo
from openprocurement.api.procedure.types import ListType
from openprocurement.contracting.core.procedure.models.contact import ContactPoint
from openprocurement.tender.core.procedure.utils import tender_created_after


class Address(BaseAddress):
    def validate_countryName(self, data, value):
        if tender_created_after(VALIDATE_ADDRESS_FROM):
            super().validate_countryName(self, data, value)

    def validate_region(self, data, value):
        if tender_created_after(VALIDATE_ADDRESS_FROM):
            super().validate_region(self, data, value)


class Organization(Model):
    """An organization."""

    name = StringType(required=True)
    name_en = StringType()
    name_ru = StringType()
    identifier = ModelType(Identifier, required=True)
    additionalIdentifiers = ListType(ModelType(Identifier))
    additionalContactPoints = ListType(ModelType(ContactPoint, required=True), required=False)
    address = ModelType(Address)
    contactPoint = ModelType(ContactPoint)
    contract_owner = StringType()


class Supplier(Organization):
    scale = StringType(choices=ORGANIZATION_SCALE_CHOICES)
    signerInfo = ModelType(SignerInfo)


class Buyer(Organization):
    kind = StringType(choices=PROCURING_ENTITY_KIND_CHOICES)
    signerInfo = ModelType(SignerInfo)
