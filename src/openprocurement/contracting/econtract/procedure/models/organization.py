from schematics.types import EmailType, StringType
from schematics.types.compound import ModelType

from openprocurement.api.procedure.models.address import Address
from openprocurement.api.procedure.models.base import Model
from openprocurement.api.procedure.models.contact import validate_telephone
from openprocurement.api.procedure.models.identifier import Identifier
from openprocurement.api.procedure.types import ListType
from openprocurement.contracting.core.procedure.models.contact import ContactPoint


class SignerInfo(Model):
    name = StringType(min_length=1, required=True)
    email = EmailType(min_length=1, required=True)
    telephone = StringType(min_length=1, required=True)
    iban = StringType(min_length=15, max_length=33, required=True)
    position = StringType(min_length=1, required=True)
    authorizedBy = StringType(min_length=1, required=True)

    def validate_telephone(self, data, value):
        validate_telephone(value)


class Organization(Model):
    """An organization."""

    name = StringType(required=True)
    name_en = StringType()
    name_ru = StringType()
    identifier = ModelType(Identifier, required=True)
    additionalIdentifiers = ListType(ModelType(Identifier))
    additionalContactPoints = ListType(ModelType(ContactPoint, required=True), required=False)
    address = ModelType(Address)
    signerInfo = ModelType(SignerInfo)
