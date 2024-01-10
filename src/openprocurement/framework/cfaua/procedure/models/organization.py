from schematics.types import StringType

from openprocurement.api.constants import SCALE_CODES
from openprocurement.api.procedure.models.organization import (
    BusinessOrganization as BaseBusinessOrganization,
)


class ContractBusinessOrganization(BaseBusinessOrganization):
    scale = StringType(choices=SCALE_CODES)
