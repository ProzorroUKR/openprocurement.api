from schematics.types import StringType

from openprocurement.api.procedure.models.organization import ProcuringEntityKind
from openprocurement.tender.core.procedure.models.organization import (
    ProcuringEntity as BaseProcuringEntity,
)

PROCURING_ENTITY_KIND_CHOICES = (
    ProcuringEntityKind.AUTHORITY.value,
    ProcuringEntityKind.CENTRAL.value,
    ProcuringEntityKind.DEFENSE.value,
    ProcuringEntityKind.GENERAL.value,
    ProcuringEntityKind.SOCIAL.value,
    ProcuringEntityKind.SPECIAL.value,
)


class ProcuringEntity(BaseProcuringEntity):
    kind = StringType(choices=PROCURING_ENTITY_KIND_CHOICES, required=True)
