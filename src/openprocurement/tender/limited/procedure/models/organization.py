from openprocurement.api.procedure.models.address import Address
from openprocurement.api.procedure.models.identifier import Identifier
from openprocurement.api.procedure.models.organization import Organization as BaseOrganization
from openprocurement.tender.core.procedure.models.contact import ContactPoint


class ReportingFundOrganization(BaseOrganization):
    identifier: Identifier | None = None
    address: Address | None = None
    contactPoint: ContactPoint | None = None
