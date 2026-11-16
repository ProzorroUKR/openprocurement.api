from typing import Literal

from openprocurement.api.procedure.models.base import Model


class BankAccount(Model):
    id: str
    scheme: Literal["IBAN"]
