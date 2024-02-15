import standards
from schematics.exceptions import ValidationError
from schematics.types import EmailType, StringType

from openprocurement.api.procedure.models.base import Model
from openprocurement.api.procedure.models.organization import (
    Organization as BaseOrganization,
)
from openprocurement.api.procedure.types import ListType, ModelType
from openprocurement.framework.core.procedure.models.address import FullAddress
from openprocurement.framework.core.procedure.models.contact import (
    ContactPoint as BaseContactPoint,
)
from openprocurement.framework.core.procedure.models.identifier import Identifier

AUTHORIZED_CPB = standards.load("organizations/authorized_cpb.json")


class ContactPoint(BaseContactPoint):
    email = EmailType(required=True)


class PatchContactPoint(ContactPoint):
    name = StringType()
    email = EmailType()


class CentralProcuringEntity(BaseOrganization):
    identifier = ModelType(Identifier, required=True)
    additionalIdentifiers = ListType(ModelType(Identifier))
    address = ModelType(FullAddress, required=True)
    contactPoint = ModelType(ContactPoint, required=True)
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


class PatchActiveCentralProcuringEntity(Model):
    contactPoint = ModelType(PatchContactPoint)
