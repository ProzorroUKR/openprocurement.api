from schematics.types import StringType

from openprocurement.api.procedure.models.organization import BusinessOrganization as BaseBusinessOrganization


class PQShortlistedFirm(BaseBusinessOrganization):
    id = StringType()
    status = StringType()
