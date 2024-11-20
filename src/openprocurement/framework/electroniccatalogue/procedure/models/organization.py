import standards
from schematics.exceptions import ValidationError
from schematics.types import StringType

from openprocurement.api.procedure.types import ModelType
from openprocurement.framework.core.procedure.models.address import FullAddress
from openprocurement.framework.core.procedure.models.contact import PatchContactPoint
from openprocurement.framework.core.procedure.models.identifier import Identifier
from openprocurement.framework.core.procedure.models.organization import (
    ProcuringEntity as BaseProcuringEntity,
)

AUTHORIZED_CPB = standards.load("organizations/authorized_cpb.json")


class CentralProcuringEntity(BaseProcuringEntity):
    kind = StringType(choices=["central"], default="central", required=True)

    def validate_identifier(self, data, identifier):
        if identifier:
            identifier_id = identifier.id
            cpb_with_statuses = {cpb["identifier"]["id"]: cpb["active"] for cpb in AUTHORIZED_CPB}
            if identifier_id not in cpb_with_statuses or not cpb_with_statuses[identifier_id]:
                raise ValidationError("Can't create framework for inactive cpb")


class PatchCentralProcuringEntity(CentralProcuringEntity):
    identifier = ModelType(Identifier)
    address = ModelType(FullAddress)
    contactPoint = ModelType(PatchContactPoint)
    name = StringType()
