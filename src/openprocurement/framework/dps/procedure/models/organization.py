import standards
from schematics.types import StringType, EmailType

from openprocurement.api.procedure.models.base import Model
from openprocurement.api.procedure.types import ListType, ModelType
from openprocurement.api.procedure.models.organization import Organization as BaseOrganization, PROCURING_ENTITY_KINDS
from openprocurement.framework.core.procedure.models.address import FullAddress
from openprocurement.framework.core.procedure.models.identifier import Identifier
from openprocurement.framework.core.procedure.models.contact import ContactPoint as BaseContactPoint

AUTHORIZED_CPB = standards.load("organizations/authorized_cpb.json")


class ContactPoint(BaseContactPoint):
    email = EmailType(required=True)


class PatchContactPoint(ContactPoint):
    name = StringType()
    email = EmailType()


class ProcuringEntity(BaseOrganization):
    identifier = ModelType(Identifier, required=True)
    additionalIdentifiers = ListType(ModelType(Identifier))
    address = ModelType(FullAddress, required=True)
    contactPoint = ModelType(ContactPoint, required=True)
    kind = StringType(choices=PROCURING_ENTITY_KINDS, default="general", required=True)

    def validate_identifier(self, data, identifier):
        pass


class PatchProcuringEntity(BaseOrganization):
    name = StringType()
    identifier = ModelType(Identifier)
    additionalIdentifiers = ListType(ModelType(Identifier))
    address = ModelType(FullAddress)
    contactPoint = ModelType(PatchContactPoint)
    kind = StringType(choices=PROCURING_ENTITY_KINDS, default="general")

    def validate_identifier(self, data, identifier):
        pass


class PatchActiveProcuringEntity(Model):
    contactPoint = ModelType(PatchContactPoint)
