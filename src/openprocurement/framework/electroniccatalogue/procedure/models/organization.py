import standards
from pydantic import field_validator

from openprocurement.api.procedure.errors import ValidationError
from openprocurement.api.procedure.models.organization import (
    ProcuringEntityKind,
)
from openprocurement.framework.core.procedure.models.address import FullAddress
from openprocurement.framework.core.procedure.models.contact import PatchContactPoint
from openprocurement.framework.core.procedure.models.identifier import Identifier
from openprocurement.framework.core.procedure.models.organization import (
    ProcuringEntity as BaseProcuringEntity,
)

AUTHORIZED_CPB = standards.load("organizations/authorized_cpb.json")


class CentralProcuringEntity(BaseProcuringEntity):
    kind: ProcuringEntityKind = ProcuringEntityKind.CENTRAL

    @field_validator("identifier")
    @classmethod
    def validate_identifier(cls, identifier):
        if identifier:
            identifier_id = identifier.id
            cpb_with_statuses = {cpb["identifier"]["id"]: cpb["active"] for cpb in AUTHORIZED_CPB}
            if identifier_id not in cpb_with_statuses or not cpb_with_statuses[identifier_id]:
                raise ValidationError("Can't create framework for inactive cpb")
        return identifier


class PatchCentralProcuringEntity(CentralProcuringEntity):
    identifier: Identifier | None = None
    address: FullAddress | None = None
    contactPoint: PatchContactPoint | None = None
    name: str | None = None
