from schematics.types import StringType

from openprocurement.api.procedure.models.organization import BusinessOrganization
from openprocurement.tender.core.procedure.models.organization import (
    ProcuringEntity as BaseProcuringEntity,
)
from openprocurement.tender.pricequotation.constants import PQ_KINDS


class ProcuringEntity(BaseProcuringEntity):
    kind = StringType(choices=PQ_KINDS, required=True)


class ShortlistedFirm(BusinessOrganization):
    id = StringType()
    status = StringType()
