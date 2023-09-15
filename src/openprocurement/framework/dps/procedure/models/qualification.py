from schematics.types import StringType

from openprocurement.framework.core.procedure.models.qualification import (
    CreateQualification as BaseCreateQualification,
    Qualification as BaseQualification,
)
from openprocurement.framework.dps.constants import DPS_TYPE


class CreateQualification(BaseCreateQualification):
    qualificationType = StringType(default=DPS_TYPE, required=True)


class Qualification(BaseQualification):
    qualificationType = StringType(default=DPS_TYPE, required=True)
