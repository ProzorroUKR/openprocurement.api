import standards
from schematics.exceptions import ValidationError
from schematics.types import StringType, EmailType

from openprocurement.api.constants import REQUIRED_FIELDS_BY_SUBMISSION_FROM
from openprocurement.api.utils import required_field_from_date
from openprocurement.api.models import (
    ModelType,
    ListType,
    Organization as BaseOrganization,
    Model,
)
from openprocurement.framework.core.procedure.models.address import Address
from openprocurement.framework.core.procedure.models.organization import (
    ContactPoint as BaseContactPoint,
    Identifier,
)


AUTHORIZED_CPB = standards.load("organizations/authorized_cpb.json")


class ContactPoint(BaseContactPoint):
    email = EmailType(required=True)


class PatchContactPoint(ContactPoint):
    name = StringType()
    email = EmailType()


class CentralProcuringEntity(BaseOrganization):
    identifier = ModelType(Identifier, required=True)
    additionalIdentifiers = ListType(ModelType(Identifier))
    address = ModelType(Address, required=True)
    contactPoint = ModelType(ContactPoint, required=True)
    kind = StringType(choices=["central"], default="central")

    def validate_identifier(self, data, identifier):
        if identifier:
            id_ = identifier.id
            cpb_with_statuses = {cpb["identifier"]["id"]: cpb["active"] for cpb in AUTHORIZED_CPB}
            if id_ not in cpb_with_statuses or not cpb_with_statuses[id_]:
                raise ValidationError("Can't create framework for inactive cpb")

    @required_field_from_date(REQUIRED_FIELDS_BY_SUBMISSION_FROM)
    def validate_kind(self, data, value):
        return value


class PatchCentralProcuringEntity(CentralProcuringEntity):
    identifier = ModelType(Identifier)
    address = ModelType(Address)
    contactPoint = ModelType(PatchContactPoint)
    name = StringType()


class PatchActiveCentralProcuringEntity(Model):
    contactPoint = ModelType(PatchContactPoint)
