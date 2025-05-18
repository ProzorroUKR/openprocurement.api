from schematics.types import EmailType, StringType

from openprocurement.api.procedure.models.base import Model
from openprocurement.api.procedure.models.contact import validate_telephone


class SignerInfo(Model):
    name = StringType(min_length=1, required=True)
    email = EmailType(min_length=1, required=True)
    telephone = StringType(min_length=1, required=True)
    iban = StringType(min_length=15, max_length=33, required=True)
    position = StringType(min_length=1, required=True)
    authorizedBy = StringType(min_length=1, required=True)

    def validate_telephone(self, data, value):
        validate_telephone(value)
