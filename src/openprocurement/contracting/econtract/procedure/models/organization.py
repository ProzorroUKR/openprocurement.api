from schematics.types import EmailType, StringType
from schematics.types.compound import ModelType

from openprocurement.api.constants import SCALE_CODES, VALIDATE_ADDRESS_FROM
from openprocurement.api.procedure.models.address import Address as BaseAddress
from openprocurement.api.procedure.models.base import Model
from openprocurement.api.procedure.models.contact import validate_telephone
from openprocurement.api.procedure.models.identifier import Identifier
from openprocurement.api.procedure.models.organization import PROCURING_ENTITY_KINDS
from openprocurement.api.procedure.types import ListType
from openprocurement.contracting.core.procedure.models.contact import ContactPoint
from openprocurement.tender.core.procedure.utils import tender_created_after


class SignerInfo(Model):
    name = StringType(min_length=1, required=True)
    email = EmailType(min_length=1, required=True)
    telephone = StringType(min_length=1, required=True)
    iban = StringType(min_length=15, max_length=33, required=True)
    position = StringType(min_length=1, required=True)
    authorizedBy = StringType(min_length=1, required=True)

    def validate_telephone(self, data, value):
        validate_telephone(value)


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
    signerInfo = ModelType(SignerInfo)


class Supplier(Organization):
    scale = StringType(choices=SCALE_CODES)


class Buyer(Organization):
    kind = StringType(choices=PROCURING_ENTITY_KINDS)
