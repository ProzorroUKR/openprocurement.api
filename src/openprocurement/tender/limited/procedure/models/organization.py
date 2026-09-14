from openprocurement.api.procedure.models.address import Address
from openprocurement.api.procedure.models.identifier import Identifier
from openprocurement.api.procedure.models.organization import Organization as BaseOrganization
from openprocurement.api.procedure.types import ModelType
from openprocurement.tender.core.procedure.models.contact import ContactPoint


class ReportingFundOrganization(BaseOrganization):
    identifier = ModelType(Identifier)  # not required
    address = ModelType(Address)  # not required
    contactPoint = ModelType(ContactPoint)  # not required
