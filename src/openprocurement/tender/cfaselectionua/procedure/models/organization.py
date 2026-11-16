from openprocurement.api.procedure.models.address import Address
from openprocurement.api.procedure.models.organization import Organization as BaseOrganization
from openprocurement.api.procedure.models.organization import OrganizationScale


class CFASelectionBusinessOrganization(BaseOrganization):
    scale: OrganizationScale | None = None
    address: Address
