from decimal import Decimal
from typing import Annotated

from openprocurement.api.procedure.models.base import Model
from openprocurement.api.procedure.types import DecimalOf


class AgreementContractParameter(Model):
    code: str
    value: Annotated[Decimal, DecimalOf(-3)]
