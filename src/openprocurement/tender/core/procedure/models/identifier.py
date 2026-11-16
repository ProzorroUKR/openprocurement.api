from typing import Any

from openprocurement.api.constants import OraCode
from openprocurement.api.procedure.models.identifier import Identifier


class PatchIdentifier(Identifier):
    scheme: OraCode | None = None
    id: Any = None


class LegislationIdentifier(Identifier):
    scheme: str | None = None
