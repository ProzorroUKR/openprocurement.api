from schematics.types import StringType

from openprocurement.api.procedure.models.base import Model


class BankAccount(Model):
    id = StringType(required=True)
    scheme = StringType(
        choices=[
            "IBAN",
        ],
        required=True,
    )
