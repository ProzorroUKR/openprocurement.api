from openprocurement.api.procedure.models.organization import BusinessOrganization as BaseBusinessOrganization


class PQShortlistedFirm(BaseBusinessOrganization):
    id: str | None = None
    status: str | None = None
