from typing import Any

from openprocurement.api.constants import OraCode
from openprocurement.api.procedure.models.base import Model
from openprocurement.api.procedure.types import Url


class Identifier(Model):
    scheme: OraCode
    id: Any
    legalName: str | None = None
    legalName_en: str | None = None
    legalName_ru: str | None = None
    uri: Url | None = None
