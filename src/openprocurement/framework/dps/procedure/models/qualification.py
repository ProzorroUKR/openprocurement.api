from schematics.types import StringType

from openprocurement.framework.core.procedure.models.qualification import (
    Qualification as BaseQualification,
)
from openprocurement.framework.dps.constants import DPS_TYPE


class Qualification(BaseQualification):
    qualificationType = StringType(default=DPS_TYPE, required=True)
