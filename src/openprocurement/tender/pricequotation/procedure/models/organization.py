from schematics.types import StringType

from openprocurement.api.procedure.models.organization import BusinessOrganization


class ShortlistedFirm(BusinessOrganization):
    id = StringType()
    status = StringType()
